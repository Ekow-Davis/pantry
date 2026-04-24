# pantry-api

Backend API for **MealWise** — a personal meal planning PWA with a focus on Ghanaian and West African cuisine.

Built with FastAPI, PostgreSQL (async via asyncpg), SQLAlchemy 2.0, and APScheduler.

---

## Project Structure

```
pantry-api/
├── app/
│   ├── api/
│   │   ├── deps.py                      # Auth dependencies (CurrentUser, CurrentAdmin)
│   │   └── v1/
│   │       ├── router.py                # Aggregates all endpoint routers
│   │       └── endpoints/
│   │           ├── auth.py              # Register, login, refresh, /me
│   │           ├── users.py             # Preferences, blacklist, pantry, history
│   │           ├── ingredients.py       # Ingredient + nutrition CRUD
│   │           ├── meals.py             # Meal library, recipes, preferences, contribute
│   │           ├── planning.py          # Daily plans, slot confirmation, meal logging
│   │           ├── recommendations.py   # Daily recommendation, pantry matches
│   │           └── admin.py             # User mgmt, meal mgmt, contributions, stats
│   ├── core/
│   │   ├── config.py                    # Pydantic settings from .env
│   │   ├── security.py                  # JWT + bcrypt
│   │   └── exceptions.py               # Custom HTTP exceptions
│   ├── db/
│   │   └── session.py                   # Async engine, session factory, Base
│   ├── models/
│   │   ├── base.py                      # Shared enums and helpers
│   │   ├── user.py                      # User model
│   │   ├── meal.py                      # Meal, MealCategory, MealCategoryMap, UserMealPreference
│   │   ├── ingredient.py                # Ingredient, IngredientNutrition
│   │   ├── recipe.py                    # MealRecipe, RecipeIngredient
│   │   ├── plan.py                      # DailyPlan, DailyPlanSlot
│   │   ├── log.py                       # MealLogEntry
│   │   ├── pantry.py                    # UserBlacklist, UserPantry
│   │   ├── contribution.py              # MealContribution
│   │   └── __init__.py                  # Imports all models (required for Alembic)
│   ├── schemas/
│   │   ├── common.py                    # MessageResponse
│   │   ├── auth.py                      # Register, login, token schemas
│   │   ├── user.py                      # UserOut, preference updates
│   │   ├── ingredient.py                # Ingredient + nutrition schemas
│   │   ├── meal.py                      # Meal, recipe, category schemas
│   │   ├── plan.py                      # Plan, slot schemas
│   │   ├── log.py                       # Meal log schemas
│   │   ├── pantry.py                    # Blacklist, pantry, match schemas
│   │   ├── contribution.py              # Contribution schemas
│   │   ├── admin.py                     # Admin stats schema
│   │   ├── recommendation.py            # Recommendation schema
│   │   └── __init__.py                  # Re-exports everything
│   ├── services/
│   │   ├── planner.py                   # Planning engine (cooldown, scoring, slot generation)
│   │   ├── nutrition.py                 # Per-serving nutrition computation
│   │   ├── recommendations.py           # Daily recommendation + pantry matcher
│   │   └── scheduler.py                 # APScheduler jobs
│   └── main.py                          # App factory, CORS, lifespan
├── alembic/
│   ├── versions/                        # Generated migration files
│   ├── env.py                           # Async migration runner (% password safe)
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

### 1. Create the database

Open a terminal and connect to PostgreSQL:

```bash
psql -U postgres
```

Inside the psql shell:

```sql
CREATE DATABASE mealwise_db;
\q
```

### 2. Set up virtual environment

```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac / Linux)
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
copy .env.example .env
```

Open `.env` and fill in at minimum:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/mealwise_db
SECRET_KEY=generate-this-below
```

**If your PostgreSQL password contains special characters**, URL-encode it first:

```bash
python -c "import urllib.parse; print(urllib.parse.quote('your_password', safe=''))"
```

Then paste the encoded version into `DATABASE_URL`.

Generate a `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(64))"
```

### 5. Run migrations

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

> **Note on the % password fix:** The Alembic `env.py` reads `DATABASE_URL`
> directly from the `.env` file rather than passing it through `alembic.ini`.
> This bypasses the `configparser` interpolation that caused the
> `ValueError: invalid interpolation syntax` error with URL-encoded passwords.

### 6. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

API: `http://localhost:8000`
Docs: `http://localhost:8000/docs` (only when `DEBUG=True`)

---

## Common Commands

| Task | Command |
|---|---|
| Start server | `uvicorn app.main:app --reload` |
| Create migration | `alembic revision --autogenerate -m "description"` |
| Apply migrations | `alembic upgrade head` |
| Rollback one step | `alembic downgrade -1` |
| Run tests | `pytest` |
| URL-encode password | `python -c "import urllib.parse; print(urllib.parse.quote('pw', safe=''))"` |
| Generate SECRET_KEY | `python -c "import secrets; print(secrets.token_hex(64))"` |

---

## API Overview

| Group | Base Path | Auth Required | Notes |
|---|---|---|---|
| Auth | `/api/v1/auth` | No (except /me) | Register, login, refresh |
| User | `/api/v1/me` | User | Preferences, blacklist, pantry, history |
| Ingredients | `/api/v1/ingredients` | User (read) / Admin (write) | Ingredient + nutrition CRUD |
| Meals | `/api/v1/meals` | User (read) / Admin (write) | Meals, recipes, preferences, contribute |
| Planning | `/api/v1/plan` | User | Daily plans, slot management, meal logging |
| Recommendations | `/api/v1/recommendations` | User | Daily novel rec, pantry matches |
| Admin | `/api/v1/admin` | Admin only | User mgmt, contributions, stats |
| Health | `/health` | No | Service health check |

---

## Background Jobs

| Job | Schedule | Description |
|---|---|---|
| End-of-day confirmation | 23:30 nightly | Auto-confirms unactioned slots for users with `assume_cooked=True` |
| Nightly maintenance | 00:05 nightly | Marks stale draft plans as completed |

Scheduler timezone: `Africa/Accra` (configurable via `SCHEDULER_TIMEZONE` in `.env`).
