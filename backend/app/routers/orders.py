from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import (
    User, RoleEnum, RestaurantTable, TableStatus,
    Order, OrderItem, MenuItem, OrderStatus, AuditLog,
)
from app.schemas.schemas import OrderCreate, OrderOut, AddItemRequest, CancelItemRequest

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _log(db, entity, entity_id, action, user_id, details=None):
    db.add(AuditLog(entity=entity, entity_id=entity_id, action=action,
                    performed_by_user_id=user_id, details=details))


@router.get("/", response_model=List[OrderOut])
def list_orders(
    status: Optional[OrderStatus] = None, table_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    if table_id:
        q = q.filter(Order.table_id == table_id)
    return q.order_by(Order.opened_at.desc()).limit(100).all()


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    table = db.query(RestaurantTable).filter(
        RestaurantTable.table_id == data.table_id, RestaurantTable.active,
    ).first()
    if not table:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    existing = db.query(Order).filter(
        Order.table_id == data.table_id,
        Order.status.notin_([OrderStatus.CERRADO]),
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="La mesa ya tiene un pedido abierto")
    order = Order(table_id=data.table_id, opened_by_user_id=current_user.user_id,
                  notes=data.notes)
    db.add(order)
    table.status = TableStatus.OCUPADA
    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order


@router.post("/{order_id}/items", response_model=OrderOut)
def add_item(order_id: int, data: AddItemRequest, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.status not in [OrderStatus.ABIERTO, OrderStatus.ENVIADO]:
        raise HTTPException(status_code=400, detail="No se puede modificar un pedido en este estado")
    item = db.query(MenuItem).filter(
        MenuItem.item_id == data.item_id, MenuItem.active, ~MenuItem.out_of_stock,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Producto no disponible")
    order_item = OrderItem(order_id=order_id, item_id=data.item_id, quantity=data.quantity,
                           notes=data.notes, unit_price_snapshot=item.price)
    db.add(order_item)
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/send-to-kitchen", response_model=OrderOut)
def send_to_kitchen(order_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.status != OrderStatus.ABIERTO:
        raise HTTPException(status_code=400, detail="El pedido ya fue enviado")
    active_items = [i for i in order.items if not i.canceled]
    if not active_items:
        raise HTTPException(status_code=400, detail="El pedido no tiene ítems")
    order.status = OrderStatus.ENVIADO
    order.sent_to_kitchen_at = datetime.utcnow()
    _log(db, "order", order_id, "SEND_TO_KITCHEN", current_user.user_id)
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/kitchen-status", response_model=OrderOut)
def update_kitchen_status(order_id: int, new_status: OrderStatus,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(require_roles(RoleEnum.COCINA, RoleEnum.ADMIN))):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    valid_transitions = {
        OrderStatus.ENVIADO: [OrderStatus.EN_PREPARACION],
        OrderStatus.EN_PREPARACION: [OrderStatus.LISTO],
        OrderStatus.LISTO: [OrderStatus.ENTREGADO],
    }
    if new_status not in valid_transitions.get(order.status, []):
        raise HTTPException(status_code=400, detail=f"Transición inválida: {order.status} -> {new_status}")
    order.status = new_status
    _log(db, "order", order_id, f"STATUS_{new_status}", current_user.user_id)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}/items/{item_id}", response_model=OrderOut)
def cancel_item(order_id: int, item_id: int, data: CancelItemRequest,
                db: Session = Depends(get_db),
                current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.MESERO))):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    order_item = db.query(OrderItem).filter(
        OrderItem.order_item_id == item_id, OrderItem.order_id == order_id,
    ).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    order_item.canceled = True
    order_item.canceled_reason = data.reason
    _log(db, "order_item", item_id, "CANCEL_ITEM", current_user.user_id, data.reason)
    db.commit()
    db.refresh(order)
    return order
