from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models, auth
from app.utils import (
    generate_otp,
    save_or_update_otp,
    send_email,
    delete_expired_otps,
)
from app.db import get_db

router = APIRouter(prefix="/otp", tags=["otp"])


@router.post("/request-otp")
def request_otp(data: schemas.SignupRequest, db: Session = Depends(get_db)):
    delete_expired_otps(db)

    if db.query(models.Admin).filter_by(email=data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    otp = generate_otp()
    hashed_pw = auth.hash_password(data.password)
    hashed_secret_key=auth.hash_password(data.secret_key)
    save_or_update_otp(
        db,
        email=data.email,
        otp=otp,
        name=data.name,
        contact=data.contact,
        restaurant_name=data.restaurant_name,
        hashed_password=hashed_pw,
        secret_key=hashed_secret_key,  # ✅ store secret_key temporarily
    )

    send_email(
        to_email=data.email,
        subject="Your OTP for Signup",
        content=f"""\nHi,

Your One-Time Password (OTP) for signing up on Notesfy is: {otp}

This OTP is valid for 3 minutes.

If you did not initiate this request, please ignore this email.

Thanks & Regards,  
Notesfy Team
"""
    )

    return {"message": "OTP sent successfully. Please verify."}


@router.post("/verify-otp")
def verify_and_register(data: schemas.OTPOnly, db: Session = Depends(get_db)):
    delete_expired_otps(db)

    record = db.query(models.EmailOTP).filter_by(email=data.email, otp=data.otp).first()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    if db.query(models.Admin).filter_by(email=data.email).first():
        raise HTTPException(status_code=400, detail="Admin already exists")

    admin = models.Admin(
        name=record.name,
        email=record.email,
        contact=record.contact,
        restaurant_name=record.restaurant_name,
        hashed_password=record.hashed_password,
        secret_key=record.secret_key,  # ✅ Save to final Admin model
        is_superuser=0,
    )

    db.add(admin)
    db.delete(record)
    db.commit()
    db.refresh(admin)

    return {"message": "Admin created successfully. Please login."}


@router.post("/request-password-otp")
def request_password_otp(data: schemas.PasswordChangeRequest, db: Session = Depends(get_db)):
    delete_expired_otps(db)

    # Check if email is registered
    if not db.query(models.Admin).filter_by(email=data.email).first():
        raise HTTPException(status_code=404, detail="Email not registered")

    otp = generate_otp()

    # Save or update OTP in DB
    save_or_update_otp(
        db,
        email=data.email,
        otp=otp
    )

    try:
        send_email(
            to_email=data.email,
            subject="Your OTP for Password Change",
            content=f"""\nHi,

Your One-Time Password (OTP) for password change is: {otp}

This OTP is valid for 3 minutes.

If you did not initiate this request, please ignore this email.

Thanks & Regards,  
JiffyMenu Team
"""
        )
    except Exception as e:
        print("Error sending email:", e)
        raise HTTPException(status_code=500, detail="Failed to send OTP email")

    return {"message": "OTP sent successfully. Please verify."}


@router.post("/verify-password-otp")
def verify_otp(data: schemas.OTPandEmailOnly, db: Session = Depends(get_db)):
    delete_expired_otps(db)

    record = db.query(models.EmailOTP).filter_by(email=data.email, otp=data.otp).first()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    admin = db.query(models.Admin).filter_by(email=data.email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin.hashed_password = auth.hash_password(data.password)
    admin.secret_key = auth.hash_password(data.secret_key)  # ✅ also update secret_key

    db.delete(record)
    db.commit()

    return {"message": "Password and secret key changed successfully. Please login."}
