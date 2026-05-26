from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import (
    User, RoleEnum, RestaurantTable, TableStatus,
    Order, OrderStatus, Bill, AuditLog,
)
from app.schemas.schemas import BillOut, PaymentRequest

router = APIRouter(prefix="/api/billing", tags=["billing"])

TAX_RATE = Decimal("0.12")


def _log(db, entity, entity_id, action, user_id, details=None):
    db.add(AuditLog(entity=entity, entity_id=entity_id, action=action,
                    performed_by_user_id=user_id, details=details))


@router.post("/orders/{order_id}/bill", response_model=BillOut)
def generate_bill(order_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(require_roles(RoleEnum.CAJERO, RoleEnum.ADMIN))):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.bill:
        return order.bill
    active_items = [i for i in order.items if not i.canceled]
    if not active_items:
        raise HTTPException(status_code=400, detail="Sin ítems activos en el pedido")
    total = sum(Decimal(str(i.unit_price_snapshot)) * i.quantity for i in active_items)
    subtotal = (total / Decimal("1.12")).quantize(Decimal("0.01"))
    tax = (total - subtotal).quantize(Decimal("0.01"))
    bill = Bill(order_id=order_id, subtotal=subtotal, tax_amount=tax, total=total,
                issued_by_user_id=current_user.user_id)
    db.add(bill)
    _log(db, "bill", order_id, "GENERATE_BILL", current_user.user_id)
    db.commit()
    db.refresh(bill)
    return bill


@router.post("/orders/{order_id}/pay", response_model=BillOut)
def pay_bill(order_id: int, data: PaymentRequest, db: Session = Depends(get_db),
             current_user: User = Depends(require_roles(RoleEnum.CAJERO, RoleEnum.ADMIN))):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    bill = order.bill
    if not bill:
        raise HTTPException(status_code=400, detail="Primero genera la cuenta")
    if bill.paid:
        raise HTTPException(status_code=400, detail="Cuenta ya fue pagada")
    if data.amount < bill.total:
        raise HTTPException(status_code=400, detail="Monto insuficiente")
    bill.paid = True
    bill.paid_at = datetime.utcnow()
    order.status = OrderStatus.CERRADO
    order.closed_at = datetime.utcnow()
    table = db.query(RestaurantTable).filter(RestaurantTable.table_id == order.table_id).first()
    if table:
        table.status = TableStatus.LIBRE
    _log(db, "bill", bill.bill_id, "PAYMENT_RECEIVED", current_user.user_id,
         f"Monto: {data.amount}")
    db.commit()
    db.refresh(bill)
    return bill


@router.get("/orders/{order_id}/bill", response_model=BillOut)
def get_bill(order_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order or not order.bill:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return order.bill
