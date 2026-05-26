import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
from app.models.user import User, RoleEnum, RestaurantTable, MenuCategory, MenuItem
from app.core.security import hash_password

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def seed_data(db):
    """Crea usuarios, mesa y menú base para pruebas."""
    admin = User(username="admin", password_hash=hash_password("admin123"),
                 full_name="Admin Test", role=RoleEnum.ADMIN)
    mesero = User(username="mesero1", password_hash=hash_password("mes123"),
                  full_name="Mesero Test", role=RoleEnum.MESERO)
    cajero = User(username="cajero1", password_hash=hash_password("caj123"),
                  full_name="Cajero Test", role=RoleEnum.CAJERO)
    cocina = User(username="cocina1", password_hash=hash_password("coc123"),
                  full_name="Cocina Test", role=RoleEnum.COCINA)
    for u in [admin, mesero, cajero, cocina]:
        db.add(u)

    table = RestaurantTable(code="M01", area="Principal", capacity=4)
    db.add(table)

    cat = MenuCategory(name="Platos")
    db.add(cat)
    db.flush()

    item = MenuItem(category_id=cat.category_id, name="Carne asada", price=100.00)
    db.add(item)
    db.commit()
    return {"admin": admin, "mesero": mesero, "cajero": cajero, "cocina": cocina,
            "table": table, "item": item}

def get_token(client, username, password):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]
