import random
from datetime import timedelta
from sqlalchemy.orm import Session
from app.models import EmailOTP
from app.models import ist_now

# ---------------- Generate OTP ----------------
def generate_otp():
    return str(random.randint(100000, 999999))

# ---------------- Save or Update OTP ----------------
def save_or_update_otp(
    db: Session,
    email: str,
    otp: str,
    name: str = None,
    contact: str = None,
    restaurant_name: str = None,
    hashed_password: str = None,
    secret_key: str = None  # ✅ Add secret_key
):
    existing = db.query(EmailOTP).filter_by(email=email).first()
    if existing:
        existing.otp = otp
        existing.created_at = ist_now()
        if name: existing.name = name
        if contact: existing.contact = contact
        if restaurant_name: existing.restaurant_name = restaurant_name
        if hashed_password: existing.hashed_password = hashed_password
        if secret_key: existing.secret_key = secret_key  # ✅ Save secret_key
    else:
        new_otp = EmailOTP(
            email=email,
            otp=otp,
            created_at=ist_now(),
            name=name,
            contact=contact,
            restaurant_name=restaurant_name,
            hashed_password=hashed_password,
            secret_key=secret_key  # ✅ Save secret_key
        )
        db.add(new_otp)

    db.commit()

# ---------------- OTP Validation ----------------
def is_otp_valid(db: Session, email: str, otp: str):
    record = db.query(EmailOTP).filter_by(email=email, otp=otp).first()
    if not record:
        return False
    return (ist_now() - record.created_at) <= timedelta(minutes=3)

# ---------------- Delete Expired OTPs ----------------
def delete_expired_otps(db: Session):
    threshold = ist_now() - timedelta(minutes=3)
    db.query(EmailOTP).filter(EmailOTP.created_at < threshold).delete()
    db.commit()

# ---------------- Email Sending ----------------
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.auth import SENDGRID_API_KEY, FROM_EMAIL

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.auth import SENDGRID_API_KEY, FROM_EMAIL
from fastapi import HTTPException

def send_email(to_email: str, subject: str, content: str):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code >= 400:
            raise Exception(f"Failed to send email. Status code: {response.status_code}")

        return {"message": "Email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SendGrid email error: {e}")
