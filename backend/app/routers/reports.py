from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import RoleEnum, Bill, Order, OrderItem, MenuItem, AuditLog
from app.schemas.schemas import AuditLogOut

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/sales")
def sales_report(date_from: Optional[date] = None, date_to: Optional[date] = None,
                 db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    q = db.query(Bill).filter(Bill.paid == True)
    if date_from:
        q = q.filter(func.date(Bill.paid_at) >= date_from)
    if date_to:
        q = q.filter(func.date(Bill.paid_at) <= date_to)
    bills = q.all()
    total_sales = sum(float(b.total) for b in bills)
    total_tax = sum(float(b.tax_amount) for b in bills)
    return {
        "period": {"from": str(date_from), "to": str(date_to)},
        "count": len(bills),
        "total_sales": round(total_sales, 2),
        "total_tax": round(total_tax, 2),
        "subtotal": round(total_sales - total_tax, 2),
    }

@router.get("/top-products")
def top_products(date_from: Optional[date] = None, date_to: Optional[date] = None,
                 limit: int = Query(10, ge=1, le=50),
                 db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    q = (db.query(MenuItem.name,
                  func.sum(OrderItem.quantity).label("total_qty"),
                  func.sum(OrderItem.quantity * OrderItem.unit_price_snapshot).label("total_amount"))
         .join(OrderItem, OrderItem.item_id == MenuItem.item_id)
         .join(Order, Order.order_id == OrderItem.order_id)
         .filter(OrderItem.canceled == False, Order.status == "CERRADO"))
    if date_from:
        q = q.filter(func.date(Order.closed_at) >= date_from)
    if date_to:
        q = q.filter(func.date(Order.closed_at) <= date_to)
    results = q.group_by(MenuItem.item_id).order_by(func.sum(OrderItem.quantity).desc()).limit(limit).all()
    return [{"name": r.name, "qty": int(r.total_qty), "amount": round(float(r.total_amount), 2)} for r in results]

@router.get("/audit", response_model=List[AuditLogOut])
def audit_logs(date_from: Optional[date] = None, date_to: Optional[date] = None,
               action: Optional[str] = None,
               db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    q = db.query(AuditLog)
    if date_from:
        q = q.filter(func.date(AuditLog.created_at) >= date_from)
    if date_to:
        q = q.filter(func.date(AuditLog.created_at) <= date_to)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    return q.order_by(AuditLog.created_at.desc()).limit(200).all()
