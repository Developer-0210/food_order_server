# get_current_admin.py

from fastapi import Depends, HTTPException, status
from app.auth import verify_token  # assuming you have this
from app.models import Admin
from app.db import get_db
from sqlalchemy.orm import Session

def get_current_admin(db: Session = Depends(get_db), token: str = Depends(verify_token)) -> Admin:
    admin = db.query(Admin).filter(Admin.email == token.email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin
