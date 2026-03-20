# detroit-family-home-care-api

Detroit Family Home Care — FastAPI backend with DFHC scaffold

## Stack

- **Python 3.11** + FastAPI
- **SQLAlchemy** ORM + Alembic migrations
- **PostgreSQL** (production) / SQLite (CI/testing)
- **JWT** authentication (python-jose + bcrypt)
- **Docker** + docker-compose
- **GitHub Actions** CI (lint-and-test)

---

## Required Environment Variables

Set these in your deployment platform (Render, Railway, etc.) before starting the app.

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | **Yes** | JWT signing key. Min 32 chars. Generate with: `openssl rand -hex 32` |
| `DATABASE_URL` | **Yes** | PostgreSQL connection string. Example: `postgresql://user:pass@host:5432/dbname` |
| `TESTING` | No | Set to `true` only in CI/test environments. Enables SQLite fallback and `create_all()`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | JWT expiry in minutes. Default: `30` |

> **Warning:** Never set `TESTING=true` in production. It disables production-safety checks.

---

## Local Development

```bash
# Copy and fill in your local values
cp .env.example .env

# Start the full stack (API + PostgreSQL)
docker-compose up --build

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## Database Migrations (Production)

This app uses **Alembic** for production schema management.

> **Important:** `Base.metadata.create_all()` is only run in `TESTING` mode (CI).
> In production, always run migrations before starting the server:

```bash
alembic upgrade head
uvicorn dfhc.main:app --host 0.0.0.0 --port 8000
```

For Railway/Render, add this as a pre-deploy command or a startup script.

> **TODO (tracked):** Alembic `alembic.ini` + `env.py` + initial migration file need to be added before first production deploy.

---

## Deployment (Render / Railway)

1. Connect this GitHub repo to your platform
2. Set the required environment variables above
3. Set the start command to:
   ```
   alembic upgrade head && uvicorn dfhc.main:app --host 0.0.0.0 --port 8000
   ```
4. Provision a PostgreSQL database and copy its URL to `DATABASE_URL`
5. Generate a strong secret: `openssl rand -hex 32` → set as `SECRET_KEY`

---

## Security & Contributing

- See [SECURITY.md](./SECURITY.md) for vulnerability reporting.
- See [docs/BRANCH_PROTECTION.md](./docs/BRANCH_PROTECTION.md) for required branch protection settings.
- See [docs/SECURITY_NOTES.md](./docs/SECURITY_NOTES.md) for threat model and security notes.
