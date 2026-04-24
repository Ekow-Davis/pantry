# pantry-api

Backend API for **MealWise** — a personal meal planning PWA with a focus on Ghanaian and West African cuisine.

Built with FastAPI, PostgreSQL (async), SQLAlchemy, and APScheduler.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL via asyncpg |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | JWT (python-jose + passlib bcrypt) |
| Rate limiting | slowapi |
| Background jobs | APScheduler |
| Email | Resend |
| Image storage | Cloudinary |

---

## Project Structure

```
pantry-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Register, login, refresh, /me
│   │       │   ├── users.py         # Preferences, blacklist, pantry, history
│   │       │   ├── meals.py         # Meal library, contribute
│   │       │   ├── planning.py      # Daily plan, slot confirmation, log
│   │       │   ├── recommendations.py  # Daily rec, pantry matches
│   │       │   └── admin.py         # Contributions, users, stats
│   │       └── router.py
│   │   └── deps.py                  # Auth dependencies (CurrentUser, CurrentAdmin)
│   ├── core/
│   │   ├── config.py                # Pydantic settings from .env
│   │   ├── security.py              # JWT + bcrypt utilities
│   │   └── exceptions.py            # Custom HTTP exceptions
│   ├── db/
│   │   └── session.py               # Async engine, session factory, Base
│   ├── models/
│   │   └── models.py                # All SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py               # All Pydantic request/response schemas
│   ├── services/
│   │   ├── planner.py               # Planning engine (cooldown, scoring, slot generation)
│   │   ├── nutrition.py             # Per-serving nutrition computation
│   │   ├── recommendations.py       # Daily recommendation + pantry matcher
│   │   └── scheduler.py             # APScheduler jobs (end-of-day, nightly)
│   └── main.py                      # App factory, CORS, lifespan
├── alembic/
│   ├── versions/                    # Migration files (generated)
│   ├── env.py
│   └── script.py.mako
├── tests/
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## Local Setup

### 1. Prerequisites

- Python 3.12
- PostgreSQL installed and running locally

### 2. Create the database

Open a terminal and connect to PostgreSQL:

```bash
psql -U postgres
```

Then run these commands inside the psql shell:

```sql
CREATE DATABASE mealwise_db;
CREATE USER mealwise_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE mealwise_db TO mealwise_user;
\q
```

> You can also just use the default `postgres` user for local development.
> In that case your DATABASE_URL would be:
> `postgresql+asyncpg://postgres:yourpassword@localhost:5432/mealwise_db`

### 3. Clone and set up the virtual environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in at minimum:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/mealwise_db
SECRET_KEY=run-python-secrets-token-hex-64-and-paste-here
```

To generate a SECRET_KEY:

```bash
python -c "import secrets; print(secrets.token_hex(64))"
```

### 6. Run database migrations

```bash
# Generate the initial migration from your models
alembic revision --autogenerate -m "initial schema"

# Apply migrations to the database
alembic upgrade head
```

### 7. Start the development server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

---

## Common Commands

| Task | Command |
|---|---|
| Start server | `uvicorn app.main:app --reload` |
| Create migration | `alembic revision --autogenerate -m "description"` |
| Apply migrations | `alembic upgrade head` |
| Rollback one step | `alembic downgrade -1` |
| Run tests | `pytest` |
| Generate SECRET_KEY | `python -c "import secrets; print(secrets.token_hex(64))"` |

---

## API Overview

| Group | Base Path | Description |
|---|---|---|
| Auth | `/api/v1/auth` | Register, login, refresh, /me |
| User | `/api/v1/me` | Preferences, blacklist, pantry, history |
| Meals | `/api/v1/meals` | Meal library, contribute |
| Planning | `/api/v1/plan` | Daily plans, slot management, meal logging |
| Recommendations | `/api/v1/recommendations` | Daily novel recommendation, pantry matches |
| Admin | `/api/v1/admin` | Contributions queue, users, stats |
| Health | `/health` | Service health check |

Full interactive documentation is available at `/docs` when `DEBUG=True`.

---

## Background Jobs

Two scheduled jobs run automatically:

| Job | Schedule | Description |
|---|---|---|
| End-of-day confirmation | 23:30 nightly | Auto-confirms unactioned plan slots for users with `assume_cooked=True` |
| Nightly maintenance | 00:05 nightly | Marks stale draft plans as completed |

Scheduler timezone defaults to `Africa/Accra` and is configurable via `SCHEDULER_TIMEZONE` in `.env`.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | PostgreSQL async connection string |
| `SECRET_KEY` | Yes | — | JWT signing key — generate a fresh one |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Refresh token lifetime |
| `DEBUG` | No | `False` | Enables SQL logging and /docs |
| `ALLOWED_ORIGINS` | No | `localhost:5173` | Comma-separated CORS origins |
| `SCHEDULER_TIMEZONE` | No | `Africa/Accra` | Timezone for scheduled jobs |
| `RESEND_API_KEY` | No | — | For transactional emails |
| `CLOUDINARY_*` | No | — | For meal photo uploads |
