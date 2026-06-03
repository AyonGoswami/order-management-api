from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Authentication Schema

class RegisterRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = "customer"


class LoginRequest(BaseModel):
    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Product Schema

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str = ""
    category: str = ""
    tags: str = ""
    price: float
    currency: str = "USD"
    stock: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: str
    category: str
    tags: str
    price: float
    currency: str
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SuggestMetadataRequest(BaseModel):
    product_name: str


class SuggestMetadataResponse(BaseModel):
    description: str
    tags: list[str]
    category: str


# ── Order schemas ──

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]
    currency: str = "USD"


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    sku_snapshot: str
    unit_price_snapshot: float
    quantity: int
    line_total: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    status: str
    total_amount: float
    currency: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str
