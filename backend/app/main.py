from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app.routers import auth, users, tables, menu, orders, billing, reports
from app.models import user  # noqa

Base.metadata.create_all(bind=engine)


def run_seed_if_empty():
    from app.models.user import User, RestaurantTable, MenuCategory, MenuItem, RoleEnum
    from app.core.security import hash_password
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        users_data = [
            ("admin", "admin123", "Administrador", RoleEnum.ADMIN),
            ("host1", "host123", "María Host", RoleEnum.HOST),
            ("mesero1", "mesero123", "Carlos Mesero", RoleEnum.MESERO),
            ("cocina1", "cocina123", "Chef Juan", RoleEnum.COCINA),
            ("cajero1", "cajero123", "Ana Cajero", RoleEnum.CAJERO),
        ]
        for username, pwd, name, role in users_data:
            db.add(User(username=username, password_hash=hash_password(pwd),
                        full_name=name, role=role))
        for i in range(1, 11):
            code = f"M{i:02d}"
            area = "Terraza" if i > 7 else "Principal"
            db.add(RestaurantTable(code=code, area=area, capacity=4 if i <= 5 else 6))
        categories = ["Entradas", "Platos Fuertes", "Bebidas", "Postres"]
        cat_objs = {}
        for cname in categories:
            cat = MenuCategory(name=cname)
            db.add(cat)
            db.flush()
            cat_objs[cname] = cat
        items = [
            ("Entradas", "Sopa del día", 35.00),
            ("Entradas", "Ensalada César", 45.00),
            ("Entradas", "Pan con ajo", 25.00),
            ("Platos Fuertes", "Carne asada", 120.00),
            ("Platos Fuertes", "Pollo a la plancha", 95.00),
            ("Platos Fuertes", "Pasta Alfredo", 85.00),
            ("Platos Fuertes", "Filete de pescado", 110.00),
            ("Bebidas", "Agua pura", 15.00),
            ("Bebidas", "Refresco", 20.00),
            ("Bebidas", "Jugo natural", 30.00),
            ("Bebidas", "Café", 18.00),
            ("Postres", "Pastel de chocolate", 45.00),
            ("Postres", "Helado 3 bolas", 35.00),
        ]
        for cat_name, item_name, price in items:
            cat = cat_objs.get(cat_name)
            if cat:
                db.add(MenuItem(category_id=cat.category_id, name=item_name, price=price))
        db.commit()
        print("✅ Seed completado automáticamente")
    except Exception as e:
        db.rollback()
        print(f"❌ Error en seed: {e}")
    finally:
        db.close()


run_seed_if_empty()

app = FastAPI(title="Sistema Gestión Restaurante", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tables.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(billing.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"status": "ok", "app": "Sistema Gestión Restaurante v1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
