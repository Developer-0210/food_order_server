from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.db import get_db
from app.auth import get_current_admin

router = APIRouter(prefix="/menu", tags=["Menu"])


# ---------- CREATE MENU ITEM ----------
@router.post("/", response_model=schemas.MenuItemOut)
def create_menu_item(
    item: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # Handle category
    category = None
    if item.food_category_name:
        category = db.query(models.FoodCategory).filter_by(
            name=item.food_category_name.strip().lower(),
            admin_id=current_admin.id
        ).first()
        if not category:
            category = models.FoodCategory(
                name=item.food_category_name.strip().lower(),
                admin_id=current_admin.id
            )
            db.add(category)
            db.commit()
            db.refresh(category)
    elif item.food_category_id:
        category = db.query(models.FoodCategory).filter_by(
            id=item.food_category_id,
            admin_id=current_admin.id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")

    # Create MenuItem
    menu_item = models.MenuItem(
        name=item.name,
        food_category_id=category.id if category else None,
        is_available=item.is_available if item.is_available is not None else True,
        admin_id=current_admin.id
    )
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)

    # Create Quantity Prices
    for qp in item.quantity_prices:
        price_entry = models.MenuItemQuantityPrice(
            menu_item_id=menu_item.id,
            quantity_type=qp.quantity_type,
            price=qp.price
        )
        db.add(price_entry)
    db.commit()
    db.refresh(menu_item)

    return menu_item


# ---------- GET MENU ITEMS FOR CURRENT ADMIN ----------
@router.get("/", response_model=List[schemas.MenuItemOut])
def get_menu_for_admin(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    items = db.query(models.MenuItem).filter(models.MenuItem.admin_id == current_admin.id).all()
    return items


# ---------- GET MENU ITEMS BY TABLE ID (PUBLIC) ----------
@router.get("/public/by-table-id/{table_id}", response_model=List[schemas.MenuItemOut])
def get_menu_by_table_id(
    table_id: int,
    db: Session = Depends(get_db)
):
    table = db.query(models.Table).filter(models.Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    items = db.query(models.MenuItem).filter(models.MenuItem.admin_id == table.admin_id).all()
    return items


# ---------- GET CATEGORIES BY TABLE ID ----------
@router.get("/public/categories/by-table-id/{table_id}", response_model=List[schemas.FoodCategoryOut])
def get_categories_by_table_id(
    table_id: int,
    db: Session = Depends(get_db)
):
    table = db.query(models.Table).filter(models.Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    categories = db.query(models.FoodCategory).filter(models.FoodCategory.admin_id == table.admin_id).all()
    return categories


# ---------- UPDATE MENU ITEM ----------
@router.put("/{item_id}", response_model=schemas.MenuItemOut)
def update_menu_item(
    item_id: int,
    item: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == item_id,
        models.MenuItem.admin_id == current_admin.id
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # Handle category again
    category = None
    if item.food_category_name:
        category = db.query(models.FoodCategory).filter_by(
            name=item.food_category_name.strip().lower(),
            admin_id=current_admin.id
        ).first()
        if not category:
            category = models.FoodCategory(
                name=item.food_category_name.strip().lower(),
                admin_id=current_admin.id
            )
            db.add(category)
            db.commit()
            db.refresh(category)
    elif item.food_category_id:
        category = db.query(models.FoodCategory).filter_by(
            id=item.food_category_id,
            admin_id=current_admin.id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")

    # Update basic fields
    db_item.name = item.name
    db_item.food_category_id = category.id if category else None
    db_item.is_available = item.is_available if item.is_available is not None else True

    db.commit()

    # Delete existing quantity prices
    db.query(models.MenuItemQuantityPrice).filter_by(menu_item_id=db_item.id).delete()

    # Add new quantity prices
    for qp in item.quantity_prices:
        price_entry = models.MenuItemQuantityPrice(
            menu_item_id=db_item.id,
            quantity_type=qp.quantity_type,
            price=qp.price
        )
        db.add(price_entry)
    db.commit()
    db.refresh(db_item)

    return db_item


# ---------- DELETE MENU ITEM ----------
@router.delete("/{item_id}")
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == item_id,
        models.MenuItem.admin_id == current_admin.id
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(db_item)
    db.commit()
    return {"message": f"Item {item_id} deleted successfully."}
