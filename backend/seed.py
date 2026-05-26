"""
Ejecutar: python seed.py
Crea el usuario admin y datos de ejemplo.
"""
from app.core.database import SessionLocal, Base, engine
from app.models.user import User, RestaurantTable, MenuCategory, MenuItem, RoleEnum
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed():
    # Users
    users_data = [
        ("admin",   "admin123",   "Administrador",   RoleEnum.ADMIN),
        ("host1",   "host123",    "María Host",      RoleEnum.HOST),
        ("mesero1", "mesero123",  "Carlos Mesero",   RoleEnum.MESERO),
        ("cocina1", "cocina123",  "Chef Juan",       RoleEnum.COCINA),
        ("cajero1", "cajero123",  "Ana Cajero",      RoleEnum.CAJERO),
    ]
    for username, pwd, name, role in users_data:
        if not db.query(User).filter(User.username == username).first():
            db.add(User(username=username, password_hash=hash_password(pwd), full_name=name, role=role))

    # Tables
    for i in range(1, 11):
        code = f"M{i:02d}"
        area = "Terraza" if i > 7 else "Principal"
        if not db.query(RestaurantTable).filter(RestaurantTable.code == code).first():
            db.add(RestaurantTable(code=code, area=area, capacity=4 if i <= 5 else 6))

    # Menu categories
    categories = ["Entradas", "Platos Fuertes", "Bebidas", "Postres"]
    cat_objs = {}
    for cname in categories:
        cat = db.query(MenuCategory).filter(MenuCategory.name == cname).first()
        if not cat:
            cat = MenuCategory(name=cname)
            db.add(cat)
            db.flush()
        cat_objs[cname] = cat

    db.flush()

    # Menu items
    items = [
        ("Entradas",       "Sopa del día",          35.00),
        ("Entradas",       "Ensalada César",         45.00),
        ("Entradas",       "Pan con ajo",            25.00),
        ("Platos Fuertes", "Carne asada",           120.00),
        ("Platos Fuertes", "Pollo a la plancha",     95.00),
        ("Platos Fuertes", "Pasta Alfredo",          85.00),
        ("Platos Fuertes", "Filete de pescado",     110.00),
        ("Bebidas",        "Agua pura",              15.00),
        ("Bebidas",        "Refresco",               20.00),
        ("Bebidas",        "Jugo natural",           30.00),
        ("Bebidas",        "Café",                   18.00),
        ("Postres",        "Pastel de chocolate",    45.00),
        ("Postres",        "Helado 3 bolas",         35.00),
    ]
    for cat_name, item_name, price in items:
        cat = cat_objs.get(cat_name)
        if cat and not db.query(MenuItem).filter(MenuItem.name == item_name).first():
            db.add(MenuItem(category_id=cat.category_id, name=item_name, price=price))

    db.commit()
    print("✅ Seed completado. Usuarios creados:")
    print("  admin / admin123  (ADMIN)")
    print("  host1 / host123   (HOST)")
    print("  mesero1 / mesero123 (MESERO)")
    print("  cocina1 / cocina123 (COCINA)")
    print("  cajero1 / cajero123 (CAJERO)")

if __name__ == "__main__":
    seed()
    db.close()
