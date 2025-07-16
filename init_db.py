# filename: create_superuser.py

from app.db import Base, engine, SessionLocal
from app.models import Admin
from app.auth import hash_password
from sqlalchemy.exc import SQLAlchemyError

def init():
    db = SessionLocal()

    try:
    

        # Superuser creation
        email = "jiffymenu@gmail.com"
        if not db.query(Admin).filter(Admin.email == email).first():
            superuser = Admin(
                name="Super Admin",
                email=email,
                contact="9999999999",  # ✅ Added
                restaurant_name="Main HQ",  # ✅ Added
                hashed_password=hash_password("asdfgh123@$"),
                secret_key=hash_password("12345"),
                is_superuser=1
            )
            db.add(superuser)
            db.commit()
            print(f"🛡️ Superuser created: {email} / asdfgh123@$")
        else:
            print("⚠️ Superuser already exists.")

    except SQLAlchemyError as e:
        print("❌ Error:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init()
