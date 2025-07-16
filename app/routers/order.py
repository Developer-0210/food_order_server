from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app import models, schemas
from app.db import get_db
from app.auth import get_current_admin

router = APIRouter(prefix="/orders", tags=["Orders"])

# ✅ Order creation without authentication, using table_id only
@router.post("/", response_model=Dict)
def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(get_db)
):
    table = db.query(models.Table).filter(models.Table.id == order_data.table_id).first()
    if not table:
        raise HTTPException(status_code=400, detail="Invalid table ID")

    admin_id = table.admin_id
    order = models.Order(table_id=table.id, admin_id=admin_id)
    db.add(order)
    db.commit()
    db.refresh(order)

    total_amount = 0.0

    for item in order_data.items:
        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == item.menu_item_id,
            models.MenuItem.admin_id == admin_id
        ).first()

        if not menu_item:
            continue

        # Look for matching quantity_type pricing
        price_entry = next(
            (qp for qp in menu_item.quantity_prices if qp.quantity_type == item.selected_type),
            None
        )

        if not price_entry:
            raise HTTPException(
                status_code=400,
                detail=f"Selected quantity type '{item.selected_type}' not available for item '{menu_item.name}'"
            )

        unit_price = price_entry.price
        item_total = unit_price * item.quantity
        total_amount += item_total

        order_item = models.OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=item.quantity,
            selected_type=item.selected_type,
            price_at_order=unit_price
        )
        db.add(order_item)

    order.total_amount = total_amount
    db.commit()
    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "table_number": table.table_number,
    }


# 🔒 Admin-protected endpoints below

@router.get("/", response_model=List[schemas.OrderOut])
def get_orders(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    return db.query(models.Order).filter(models.Order.admin_id == current_admin.id).all()


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    estimated_time: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.admin_id == current_admin.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status

    if estimated_time is not None:
        order.estimated_time = estimated_time

    db.commit()
    return {"message": f"Order {order_id} updated to '{status}'."}


@router.delete("/{order_id}", response_model=Dict)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.admin_id == current_admin.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    db.commit()

    return {"message": f"Order {order_id} deleted successfully"}




from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.db import get_db
from app.auth import get_current_admin
from typing import List
from datetime import datetime, timedelta
@router.get("/poll-new-orders")
def poll_new_orders(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # Optionally: filter only recent orders in last 10 seconds
    recent_time = datetime.utcnow() - timedelta(seconds=10)
    
    orders = db.query(models.Order).filter(
        models.Order.admin_id == current_admin.id,
        models.Order.created_at >= recent_time
    ).all()

    return {
        "orders": [
            {
                "id": order.id,
                "table_number": order.table.table_number,
                "created_at": order.created_at.isoformat()
            }
            for order in orders
        ]
    }

from app import models, schemas, auth
@router.get("/history", response_model=List[schemas.OrderOut])
def get_order_history_with_secret(
    secret_key_verified: bool = Depends(auth.verify_secret_key),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin),
):
    return db.query(models.Order).filter(models.Order.admin_id == current_admin.id).all()
