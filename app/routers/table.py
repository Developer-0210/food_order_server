from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.db import get_db
from app.auth import get_current_admin

router = APIRouter(prefix="/tables", tags=["Tables"])

# 🔹 Create a new table (admin-scoped)
@router.post("/", response_model=schemas.TableOut)
def create_table(
    table: schemas.TableCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # Ensure unique table number for this admin
    existing = db.query(models.Table).filter(
        models.Table.admin_id == current_admin.id,
        models.Table.table_number == table.table_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Table number already exists.")

    table_obj = models.Table(**table.dict(), admin_id=current_admin.id)
    db.add(table_obj)
    db.commit()
    db.refresh(table_obj)
    return table_obj

# 🔹 Get tables of the current admin
@router.get("/", response_model=List[schemas.TableOut])
def get_tables(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    return db.query(models.Table).filter(models.Table.admin_id == current_admin.id).all()

# 🔹 Public endpoint to get all tables (used only if superuser/frontend needs it)
@router.get("/public", response_model=List[schemas.TableOut])
def get_all_tables(db: Session = Depends(get_db)):
    return db.query(models.Table).all()

# 🔹 Update a table (admin-scoped)
@router.put("/{table_id}", response_model=schemas.TableOut)
def update_table(
    table_id: int,
    table: schemas.TableCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    table_obj = db.query(models.Table).filter(
        models.Table.id == table_id,
        models.Table.admin_id == current_admin.id
    ).first()

    if not table_obj:
        raise HTTPException(status_code=404, detail="Table not found")

    table_obj.table_number = table.table_number
    db.commit()
    db.refresh(table_obj)
    return table_obj

# 🔹 Delete a table (admin-scoped)
@router.delete("/{table_id}")
def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    table_obj = db.query(models.Table).filter(
        models.Table.id == table_id,
        models.Table.admin_id == current_admin.id
    ).first()

    if not table_obj:
        raise HTTPException(status_code=404, detail="Table not found")

    db.delete(table_obj)
    db.commit()
    return {"message": f"Table {table_id} deleted."}
