# 🍴 Sistema de Gestión de Restaurante — RestaurantePRO

Sistema web completo para la gestión integral de un restaurante: mesas, pedidos, cocina y facturación.

## 🌐 Acceso en línea

**Frontend:** https://6a1b38e800af4fadd4ff265b--sistema-gestion-restaurante.netlify.app/login

**Backend API / Docs:** https://sistema-gerestaurante-backendstion.onrender.com/docs

## 👤 Usuarios de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | ADMIN |
| host1 | host123 | HOST |
| mesero1 | mesero123 | MESERO |
| cocina1 | cocina123 | COCINA |
| cajero1 | cajero123 | CAJERO |

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + Vite + React Router 6 |
| Backend | Python 3.11 + FastAPI |
| Base de datos | PostgreSQL (Render) / MySQL (local) |
| Auth | JWT + RBAC (5 roles) |
| CI/CD | GitHub Actions |
| Deploy Frontend | Netlify |
| Deploy Backend | Render |

## ✅ Funcionalidades implementadas

- Autenticación JWT con 5 roles (ADMIN, HOST, MESERO, COCINA, CAJERO)
- Mapa de mesas con estados en tiempo real (auto-refresh cada 15s)
- Gestión de pedidos: crear, agregar ítems con notas, enviar a cocina
- Pantalla KDS de cocina con flujo de estados (auto-refresh cada 10s)
- Facturación automática con desglose de IVA 12%
- Administración de menú: categorías y productos
- Gestión de usuarios y roles
- Reportes de ventas y top productos
- Bitácora de auditoría de acciones críticas

---

## 💻 Instalación y ejecución local

### Requisitos previos
- Python 3.11+
- Node.js 20+
- MySQL 8 corriendo en localhost:3306

### Backend

```bash
git clone <URL_REPOSITORIO>
cd sistema-gestion-restaurante/backend

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
Documentación Swagger: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en http://localhost:3000

---

## 🐳 Ejecución con Docker Compose

```bash
docker-compose up --build

# Primera vez, en otra terminal:
docker-compose exec backend python seed.py
```

---

## 🧪 Pruebas unitarias

```bash
cd backend
pytest tests/ --cov=app --cov-report=term-missing -v
```

Cobertura actual: **85%** — 31 pruebas pasando.

---

## ⚙️ Pipeline CI/CD

El pipeline en `.github/workflows/ci.yml` se ejecuta automáticamente en cada push a `main`:

1. **Lint** — flake8 sobre el código Python
2. **Security audit** — pip-audit sobre dependencias
3. **Tests** — pytest con reporte de cobertura (mínimo 65%)
4. **Build** — Vite compila el frontend

---

## 📁 Estructura del proyecto

```
sistema-gestion-restaurante/
├── backend/
│   ├── app/
│   │   ├── core/          # config, database, security (JWT)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── routers/       # auth, users, tables, menu, orders, billing, reports
│   ├── tests/             # 31 pruebas unitarias (pytest)
│   ├── seed.py            # Datos de ejemplo
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/         # Login, TableMap, Orders, KDS, Billing, Menu, Users, Reports
│       ├── components/    # Layout (sidebar con RBAC)
│       ├── context/       # AuthContext (JWT)
│       └── api/           # Axios client
├── .github/
│   └── workflows/
│       └── ci.yml         # Pipeline CI/CD
└── docker-compose.yml
```

---

## 📋 Información académica

**Universidad Mariano Gálvez de Guatemala**
Ingeniería en Sistemas de Información y Ciencias de la Computación
Ingeniería de Software B — Fin de semana
Catedrático: Michael Rodolfo Asturias López
Estudiante: David Edgar Recinos García — 0900-22-2697
