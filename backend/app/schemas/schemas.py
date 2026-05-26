from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.user import RoleEnum, TableStatus, OrderStatus

# ── Auth ──────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str
    user_id: int

class LoginRequest(BaseModel):
    username: str
    password: str

# ── Users ─────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: RoleEnum

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[RoleEnum] = None
    active: Optional[bool] = None
    password: Optional[str] = None

class UserOut(BaseModel):
    user_id: int
    username: str
    full_name: str
    role: RoleEnum
    active: bool
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

# ── Tables ────────────────────────────────────────────
class TableCreate(BaseModel):
    code: str
    area: str = "Principal"
    capacity: int

    @field_validator("capacity")
    @classmethod
    def capacity_positive(cls, v):
        if v <= 0:
            raise ValueError("Capacidad debe ser mayor a 0")
        return v

class TableUpdate(BaseModel):
    area: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[TableStatus] = None
    active: Optional[bool] = None

class TableOut(BaseModel):
    table_id: int
    code: str
    area: str
    capacity: int
    status: TableStatus
    active: bool
    model_config = {"from_attributes": True}

# ── Menu ──────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str

class CategoryOut(BaseModel):
    category_id: int
    name: str
    active: bool
    model_config = {"from_attributes": True}

class MenuItemCreate(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    price: Decimal

    @field_validator("price")
    @classmethod
    def price_non_negative(cls, v):
        if v < 0:
            raise ValueError("Precio no puede ser negativo")
        return v

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    active: Optional[bool] = None
    out_of_stock: Optional[bool] = None
    category_id: Optional[int] = None

class MenuItemOut(BaseModel):
    item_id: int
    category_id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    active: bool
    out_of_stock: bool
    model_config = {"from_attributes": True}

# ── Orders ────────────────────────────────────────────
class OrderItemCreate(BaseModel):
    item_id: int
    quantity: int
    notes: Optional[str] = None

class OrderItemOut(BaseModel):
    order_item_id: int
    item_id: int
    quantity: int
    notes: Optional[str] = None
    unit_price_snapshot: Decimal
    canceled: bool
    model_config = {"from_attributes": True}

class OrderCreate(BaseModel):
    table_id: int
    notes: Optional[str] = None

class OrderOut(BaseModel):
    order_id: int
    table_id: int
    status: OrderStatus
    opened_at: Optional[datetime] = None
    sent_to_kitchen_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[OrderItemOut] = []
    model_config = {"from_attributes": True}

class AddItemRequest(BaseModel):
    item_id: int
    quantity: int = 1
    notes: Optional[str] = None

class CancelItemRequest(BaseModel):
    reason: str

# ── Bill ──────────────────────────────────────────────
class BillOut(BaseModel):
    bill_id: int
    order_id: int
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    paid: bool
    issued_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class PaymentRequest(BaseModel):
    amount: Decimal

# ── Audit ─────────────────────────────────────────────
class AuditLogOut(BaseModel):
    audit_id: int
    entity: str
    entity_id: Optional[int] = None
    action: str
    details: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
