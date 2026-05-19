# ESI-GM Full Backend

A unified Django REST Framework backend for the ESI-GM laboratory management system.

## Project Structure

```
full_backend/
├── manage.py                     ← Django entry point
├── migrate_all.py                ← Script to run migrations for all apps
├── requirements.txt              ← All Python dependencies (single install)
├── db.sqlite3                    ← Single unified SQLite database
│
├── project/                      ← Core Django settings and root routing
│
└── apps/                         ← All features as modular Django apps
    ├── esi_gm/                   (projects, materials, auth, maintenance)
    ├── inventory/                (inventory & admin dashboard)
    ├── scanner/                  (QR code scanner & stock)
    ├── browse/                   (browse material catalog)
    ├── login_app/                (simple login endpoint)
    ├── transfers/                (lab-to-lab material transfers)
    └── my_request/               (student material requests)
```

## Quick Start

### 1 — Install dependencies (once)

```bash
pip install -r requirements.txt
```

### 2 — Apply all migrations

```bash
python manage.py migrate
```

### 3 — Run the backend

```bash
python manage.py runserver
```

The entire backend will run on port `8000`.

---

## API Routes

| Path Prefix | Target Application | Key Endpoints |
|-------------|--------------------|---------------|
| `/api/esi-gm/` | ESI-GM (main) | `/login/` `/register/` `/dashboard/` `/projects/` `/maintenance/` |
| `/api/inventory/` | Inventory / Admin | `/api/dashboard/stats/` `/api/materials/` `/api/requests/` |
| `/api/scanner/` | QR Scanner | `/api/materials/` `/api/transactions/scan/` |
| `/api/browse/` | Browse Catalog | `/api/materials/` `/api/categories/` |
| `/api/login/` | Login | `/api/login/` |
| `/api/transfers/` | Material Transfers | `/api/transfers/` |
| `/api/my-request/`| My Requests | `/api/requests/` `/api/login/` `/api/dashboard/` |

---

## Notes

- The project uses a **single SQLite database** (`db.sqlite3`).
- No hardcoded absolute paths — all paths use `BASE_DIR`.
- CORS is pre-configured for `localhost:3000` and `localhost:5173`.
