# Sistema de Gestión de Restaurante

Sistema web para la gestión de mesas, pedidos, cocina y facturación de un restaurante.

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + Vite + React Router |
| Backend | Python 3.11 + FastAPI |
| Base de datos | MySQL 8 (SQLite en tests) |
| Auth | JWT + RBAC (5 roles) |
| CI/CD | GitHub Actions |

<img width="3056" height="1834" alt="c4_container_nivel2" src="https://github.com/user-attachments/assets/3bdbd398-d009-4add-9e7f-ed8eb3c9573a" />

## Roles del sistema

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | ADMIN |
| host1 | host123 | HOST |
| mesero1 | mesero123 | MESERO |
| cocina1 | cocina123 | COCINA |
| cajero1 | cajero123 | CAJERO |

---

## Instalación y ejecución local

### Requisitos previos
- Python 3.11+
- Node.js 20+
- MySQL 8 corriendo en localhost:3306

### 1. Clonar el repositorio

```bash
git clone https://github.com/DavidsitoPay/sistema-gestion-restaurante.git
cd sistema-gestion-restaurante
```

### 2. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
# Crear la BD en MySQL: CREATE DATABASE restaurante_db;
# Copiar .env.example a .env y ajustar credenciales si es necesario
copy .env.example .env

# Crear tablas y cargar datos de ejemplo
python seed.py

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en http://localhost:8000  
Documentación API (Swagger): http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en http://localhost:3000

---

## Ejecución con Docker Compose

```bash
# Levantar todos los servicios (DB + Backend + Frontend)
docker-compose up --build

# Crear tablas y seed (primera vez, en otra terminal)
docker-compose exec backend python seed.py
```

---

## Pruebas unitarias

```bash
cd backend
pytest tests/ --cov=app --cov-report=term-missing -v
```

---

## Estructura del proyecto

```
sistema-gestion-restaurante/
├── backend/
│   ├── app/
│   │   ├── core/          # config, database, security (JWT)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── routers/       # auth, users, tables, menu, orders, billing, reports
│   ├── tests/             # Pruebas unitarias (pytest)
│   ├── seed.py            # Datos de ejemplo
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/         # Login, TableMap, Orders, KDS, Billing, Menu, Users, Reports
│       ├── components/    # Layout (sidebar)
│       ├── context/       # AuthContext
│       └── api/           # Axios client
├── .github/
│   └── workflows/
│       └── ci.yml         # Pipeline CI/CD (lint + tests + build)
└── docker-compose.yml
```

---

## Pipeline CI/CD

El pipeline en `.github/workflows/ci.yml` ejecuta automáticamente en cada push/PR:

1. **Lint** — flake8 sobre el código Python
2. **Tests** — pytest con reporte de cobertura
3. **Build** — construcción del frontend con Vite

---

## Funcionalidades implementadas

- ✅ Autenticación JWT con 5 roles (ADMIN, HOST, MESERO, COCINA, CAJERO)
- ✅ Mapa de mesas con estados en tiempo real
- ✅ Gestión de pedidos (crear, agregar ítems, enviar a cocina)
- ✅ Pantalla KDS de cocina con flujo de estados
- ✅ Facturación automática con desglose de IVA 12%
- ✅ Administración de menú (categorías y productos)
- ✅ Gestión de usuarios y roles
- ✅ Reportes de ventas y top productos
- ✅ Bitácora de auditoría

..
