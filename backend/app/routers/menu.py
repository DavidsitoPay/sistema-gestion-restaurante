from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import MenuCategory, MenuItem, RoleEnum
from app.schemas.schemas import CategoryCreate, CategoryOut, MenuItemCreate, MenuItemUpdate, MenuItemOut

router = APIRouter(prefix="/api/menu", tags=["menu"])

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(MenuCategory).filter(MenuCategory.active == True).all()

@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    if db.query(MenuCategory).filter(MenuCategory.name == data.name).first():
        raise HTTPException(status_code=400, detail="Categoría ya existe")
    cat = MenuCategory(name=data.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(cat_id: int, db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    cat = db.query(MenuCategory).filter(MenuCategory.category_id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    cat.active = False
    db.commit()

@router.get("/items", response_model=List[MenuItemOut])
def list_items(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(MenuItem).filter(MenuItem.active == True).all()

@router.post("/items", response_model=MenuItemOut, status_code=201)
def create_item(data: MenuItemCreate, db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    cat = db.query(MenuCategory).filter(MenuCategory.category_id == data.category_id, MenuCategory.active == True).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    item = MenuItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/items/{item_id}", response_model=MenuItemOut)
def update_item(item_id: int, data: MenuItemUpdate, db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    item = db.query(MenuItem).filter(MenuItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db), _=Depends(require_roles(RoleEnum.ADMIN))):
    item = db.query(MenuItem).filter(MenuItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    item.active = False
    db.commit()
