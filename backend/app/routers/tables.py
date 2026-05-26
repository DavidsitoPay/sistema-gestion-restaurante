from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import RoleEnum, User
from app.models.user import RestaurantTable, TableStatus, OrderStatus
from app.schemas.schemas import TableCreate, TableUpdate, TableOut

router = APIRouter(prefix="/api/tables", tags=["tables"])

ALL_STAFF = [RoleEnum.ADMIN, RoleEnum.HOST, RoleEnum.MESERO, RoleEnum.CAJERO]

@router.get("/", response_model=List[TableOut])
def list_tables(area: Optional[str] = None, status: Optional[TableStatus] = None,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(RestaurantTable).filter(RestaurantTable.active == True)
    if area:
        q = q.filter(RestaurantTable.area == area)
    if status:
        q = q.filter(RestaurantTable.status == status)
    return q.all()

@router.post("/", response_model=TableOut, status_code=201)
def create_table(data: TableCreate, db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    if db.query(RestaurantTable).filter(RestaurantTable.code == data.code).first():
        raise HTTPException(status_code=400, detail="Código de mesa ya existe")
    table = RestaurantTable(**data.model_dump())
    db.add(table)
    db.commit()
    db.refresh(table)
    return table

@router.put("/{table_id}", response_model=TableOut)
def update_table(table_id: int, data: TableUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    table = db.query(RestaurantTable).filter(RestaurantTable.table_id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(table, k, v)
    db.commit()
    db.refresh(table)
    return table

@router.delete("/{table_id}", status_code=204)
def delete_table(table_id: int, db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    from app.models.user import Order
    table = db.query(RestaurantTable).filter(RestaurantTable.table_id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    open_orders = db.query(Order).filter(Order.table_id == table_id,
                                          Order.status.notin_([OrderStatus.CERRADO])).first()
    if open_orders:
        raise HTTPException(status_code=400, detail="Mesa tiene pedidos abiertos")
    table.active = False
    db.commit()
