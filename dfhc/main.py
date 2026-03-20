import os

from fastapi import FastAPI
from dfhc.app.core.database import engine, Base
from dfhc.app.routes import users, auth

# ---------------------------------------------------------------------------
# Startup: create tables only in TESTING mode.
# In production, database schema MUST be managed via Alembic migrations:
#   alembic upgrade head
# Run migrations before starting uvicorn. Do NOT rely on create_all() in prod.
# TODO: add alembic.ini + env.py and an initial migration (tracked in #hardening)
# ---------------------------------------------------------------------------
_TESTING = os.getenv("TESTING", "").lower() in ("1", "true", "yes")

if _TESTING:
    # Safe for CI — creates tables in the test SQLite DB
    Base.metadata.create_all(bind=engine)
# Production: no create_all() — rely on 'alembic upgrade head' at deploy time.

app = FastAPI(title="DFHC API", version="0.1.0")
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "dfhc-api"}
