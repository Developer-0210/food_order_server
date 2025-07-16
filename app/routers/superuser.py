from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, auth
from app.db import get_db
from app.auth import get_current_superuser

router = APIRouter(prefix="/superuser", tags=["Superuser"])

# ---------- CREATE ADMIN ----------
@router.post("/admins", response_model=schemas.AdminOut)
def create_admin(
    admin_data: schemas.AdminCreate,
    db: Session = Depends(get_db),
    superuser: models.Admin = Depends(get_current_superuser)
):
    existing = db.query(models.Admin).filter(models.Admin.email == admin_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin with this email already exists")

    new_admin = models.Admin(
        name=admin_data.name,
        email=admin_data.email,
        contact=admin_data.contact,
        restaurant_name=admin_data.restaurant_name,
        hashed_password=auth.hash_password(admin_data.password),
        secret_key=auth.hash_password(admin_data.secret_key),
        is_superuser=admin_data.is_superuser or 0
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

# ---------- LIST ADMINS ----------
@router.get("/admins", response_model=List[schemas.AdminOut])
def list_admins(
    db: Session = Depends(get_db),
    superuser: models.Admin = Depends(get_current_superuser)
):
    return db.query(models.Admin).filter(models.Admin.is_superuser == 0).all()

# ---------- UPDATE ADMIN ----------
@router.put("/admins/{admin_id}", response_model=schemas.AdminOut)
def update_admin(
    admin_id: int,
    update_data: schemas.AdminCreate,
    db: Session = Depends(get_db),
    superuser: models.Admin = Depends(get_current_superuser)
):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id, models.Admin.is_superuser == 0).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin.name = update_data.name
    admin.email = update_data.email
    admin.contact = update_data.contact
    admin.restaurant_name = update_data.restaurant_name
    admin.hashed_password = auth.hash_password(update_data.password)
    admin.secret_key = auth.hash_password(update_data.secret_key)
    db.commit()
    db.refresh(admin)
    return admin

# ---------- DELETE ADMIN ----------
@router.delete("/admins/{admin_id}")
def delete_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    superuser: models.Admin = Depends(get_current_superuser)
):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id, models.Admin.is_superuser == 0).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    db.delete(admin)
    db.commit()
    return {"message": f"Admin with ID {admin_id} deleted."}

# ---------- SIGNUP ADMIN ----------
@router.post("/signup", response_model=schemas.AdminOut)
def signup_admin(admin_data: schemas.AdminCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Admin).filter(models.Admin.email == admin_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin with this email already exists")

    new_admin = models.Admin(
        name=admin_data.name,
        email=admin_data.email,
        contact=admin_data.contact,
        restaurant_name=admin_data.restaurant_name,
        hashed_password=auth.hash_password(admin_data.password),
        secret_key=auth.hash_password(admin_data.secret_key),
        is_superuser=0  # Regular admin, not superuser
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin
