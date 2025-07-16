from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime

# ---------- Enums ----------
class QuantityEnum(str, Enum):
    quarter = "quarter"
    half = "half"
    full = "full"

# ---------- AUTH ----------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ---------- ADMIN ----------
class AdminBase(BaseModel):
    name: str
    email: EmailStr
    contact: str
    restaurant_name: Optional[str] = None

class AdminCreate(AdminBase):
    password: str
    secret_key:str
    is_superuser: Optional[int] = 0
    restaurant_name: str  # required here

class AdminOut(AdminBase):
    id: int
    is_superuser: int
    model_config = ConfigDict(from_attributes=True)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_superuser: int
    model_config = ConfigDict(from_attributes=True)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# ---------- FOOD CATEGORY ----------
class FoodCategoryBase(BaseModel):
    name: str

class FoodCategoryCreate(FoodCategoryBase):
    pass

class FoodCategoryOut(FoodCategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- QUANTITY PRICE ----------
class QuantityPrice(BaseModel):
    quantity_type: QuantityEnum
    price: float

# ---------- MENU ITEM ----------
class MenuItemBase(BaseModel):
    name: str
    is_available: bool = True
    food_category: Optional[FoodCategoryOut]

class MenuItemCreate(BaseModel):
    name: str
    is_available: Optional[bool] = True
    food_category_name: Optional[str] = None  # To create by name
    food_category_id: Optional[int] = None    # Or by ID
    quantity_prices: List[QuantityPrice]      # Full, half, etc.

class MenuItemOut(BaseModel):
    id: int
    name: str
    is_available: bool
    food_category: Optional[FoodCategoryOut]
    quantity_prices: List[QuantityPrice]
    model_config = ConfigDict(from_attributes=True)

# ---------- TABLE ----------
class TableBase(BaseModel):
    table_number: int

class TableCreate(TableBase):
    pass

class TableOut(TableBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- ORDER ITEM ----------
class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int
    selected_type: QuantityEnum

class OrderItemOut(OrderItemCreate):
    price_at_order: float
    menu_item: MenuItemOut
    model_config = ConfigDict(from_attributes=True)

# ---------- ORDER ----------
class OrderCreate(BaseModel):
    table_id: int
    items: List[OrderItemCreate]

class OrderOut(BaseModel):
    id: int
    table_id: int
    status: str
    estimated_time: Optional[str]
    total_amount: float
    table_number: int
    created_at: datetime
    items: List[OrderItemOut]
    model_config = ConfigDict(from_attributes=True)

# ---------- EMAIL/OTP ----------
class EmailOnly(BaseModel):
    email: EmailStr

class OTPOnly(BaseModel):
    email: EmailStr
    otp: str

class PasswordChangeRequest(BaseModel):
    email: EmailStr

class OTPandEmailOnly(BaseModel):
    email: EmailStr
    otp: str
    password: str
    secret_key:str

# ---------- SIGNUP ----------
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    contact: str
    restaurant_name: str
    password: str
    secret_key:str


