from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, Enum as SqlEnum, DateTime,
    UniqueConstraint, Boolean
)
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime
import enum
from pytz import timezone

# ---------- ENUMS ----------

class QuantityEnum(str, enum.Enum):
    quarter = "quarter"
    half = "half"
    full = "full"

# ---------- ADMIN ----------
import uuid
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    restaurant_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Integer, default=0)
    secret_key = Column(String, unique=True, nullable=True, default=lambda: str(uuid.uuid4()))
    # Relationships
    menu_items = relationship("MenuItem", back_populates="admin", cascade="all, delete")
    food_categories = relationship("FoodCategory", back_populates="admin", cascade="all, delete")
    tables = relationship("Table", back_populates="admin", cascade="all, delete")
    orders = relationship("Order", back_populates="admin", cascade="all, delete")
    

# ---------- FOOD CATEGORY ----------

class FoodCategory(Base):
    __tablename__ = "food_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    admin_id = Column(Integer, ForeignKey("admins.id"))
    admin = relationship("Admin", back_populates="food_categories")

    menu_items = relationship("MenuItem", back_populates="food_category", cascade="all, delete")

# ---------- MENU ITEM ----------

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)

    food_category_id = Column(Integer, ForeignKey("food_categories.id"), nullable=False)
    food_category = relationship("FoodCategory", back_populates="menu_items")

    admin_id = Column(Integer, ForeignKey("admins.id"))
    admin = relationship("Admin", back_populates="menu_items")

    order_items = relationship("OrderItem", back_populates="menu_item", cascade="all, delete")
    quantity_prices = relationship("MenuItemQuantityPrice", back_populates="menu_item", cascade="all, delete")

    def get_allowed_quantities(self):
        return [qp.quantity_type for qp in self.quantity_prices]

    def get_price_for(self, quantity_type: str):
        for qp in self.quantity_prices:
            if qp.quantity_type == quantity_type:
                return qp.price
        return None

# ---------- MENU ITEM QUANTITY PRICE ----------

class MenuItemQuantityPrice(Base):
    __tablename__ = "menu_item_quantity_prices"

    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity_type = Column(SqlEnum(QuantityEnum), nullable=False)  # full, half, quarter
    price = Column(Float, nullable=False)

    menu_item = relationship("MenuItem", back_populates="quantity_prices")

    __table_args__ = (
        UniqueConstraint("menu_item_id", "quantity_type", name="uq_menuitem_quantitytype"),
    )

# ---------- TABLE ----------

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, nullable=False)

    admin_id = Column(Integer, ForeignKey("admins.id"))
    admin = relationship("Admin", back_populates="tables")

# ---------- ORDER ----------

def ist_now():
    return datetime.now(timezone("Asia/Kolkata"))

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"))
    admin_id = Column(Integer, ForeignKey("admins.id"))
    status = Column(String, default="pending")
    estimated_time = Column(String, nullable=True)
    total_amount = Column(Float, default=0)
    created_at = Column(DateTime, default=ist_now)

    admin = relationship("Admin", back_populates="orders")
    table = relationship("Table")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")

    @property
    def table_number(self):
        return self.table.table_number if self.table else None

# ---------- ORDER ITEM ----------

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))

    quantity = Column(Integer, nullable=False)
    selected_type = Column(SqlEnum(QuantityEnum), nullable=False)
    price_at_order = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")

# ---------- EMAIL OTP ----------

class EmailOTP(Base):
    __tablename__ = "email_otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    otp = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=ist_now)

    name = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    restaurant_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    secret_key=Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("email", name="uq_email_otp"),)

# ---------- PASSWORD OTP ----------

class PasswordOTP(Base):
    __tablename__ = "password_change_otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    otp = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=ist_now)

    __table_args__ = (UniqueConstraint("email", name="uq_password_email_otp"),)
