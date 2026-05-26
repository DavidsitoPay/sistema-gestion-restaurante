from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import auth, users, tables, menu, orders, billing, reports

# Importar todos los modelos para que SQLAlchemy los registre
from app.models import user  # noqa

Base.metadata.create_all(bind=engine)

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
