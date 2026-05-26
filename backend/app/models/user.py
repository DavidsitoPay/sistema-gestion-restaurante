from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    HOST = "HOST"
    MESERO = "MESERO"
    COCINA = "COCINA"
    CAJERO = "CAJERO"


class TableStatus(str, enum.Enum):
    LIBRE = "LIBRE"
    OCUPADA = "OCUPADA"
    PENDIENTE = "PENDIENTE"
    PAGANDO = "PAGANDO"


class OrderStatus(str, enum.Enum):
    ABIERTO = "ABIERTO"
    ENVIADO = "ENVIADO"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO = "LISTO"
    ENTREGADO = "ENTREGADO"
    CERRADO = "CERRADO"


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class RestaurantTable(Base):
    __tablename__ = "tables"
    table_id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    area = Column(String(50), default="Principal")
    capacity = Column(Integer, nullable=False)
    status = Column(Enum(TableStatus), default=TableStatus.LIBRE)
    active = Column(Boolean, default=True)
    orders = relationship("Order", back_populates="table")


class MenuCategory(Base):
    __tablename__ = "menu_categories"
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)
    active = Column(Boolean, default=True)
    items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"
    item_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("menu_categories.category_id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True)
    out_of_stock = Column(Boolean, default=False)
    category = relationship("MenuCategory", back_populates="items")


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.table_id"), nullable=False)
    opened_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.ABIERTO)
    opened_at = Column(DateTime, server_default=func.now())
    sent_to_kitchen_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    table = relationship("RestaurantTable", back_populates="orders")
    opened_by = relationship("User", foreign_keys=[opened_by_user_id])
    items = relationship("OrderItem", back_populates="order")
    bill = relationship("Bill", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.item_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    notes = Column(Text, nullable=True)
    unit_price_snapshot = Column(Numeric(10, 2), nullable=False)
    canceled = Column(Boolean, default=False)
    canceled_reason = Column(Text, nullable=True)
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")


class Bill(Base):
    __tablename__ = "bills"
    bill_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), unique=True, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    issued_at = Column(DateTime, server_default=func.now())
    issued_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)
    order = relationship("Order", back_populates="bill")
    issued_by = relationship("User")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    audit_id = Column(Integer, primary_key=True, index=True)
    entity = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    performed_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    performed_by = relationship("User")
