import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dfhc.app.core.database import engine, Base
from dfhc.app.routes import users, auth, clients

# ---------------------------------------------------------------------------
# Production startup validation
# Alembic migrations (alembic upgrade head) MUST be run before starting the
# server in production. This lifespan handler verifies required env vars are
# present at boot time and fails loudly rather than silently at request time.
# ---------------------------------------------------------------------------
_TESTING = os.getenv("TESTING", "").lower() in ("1", "true", "yes")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if _TESTING:
        # CI: create tables in the test SQLite DB so tests work without Alembic
        Base.metadata.create_all(bind=engine)
    else:
        # Production: validate required env vars at startup - fail loudly if missing
        missing = [v for v in ("DATABASE_URL", "SECRET_KEY") if not os.environ.get(v)]
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {missing}. "
                "Set them before starting the server. "
                "Schema must be applied via: alembic upgrade head"
            )
    yield
    # Shutdown: nothing to clean up at this stage


app = FastAPI(
    title="DFHC API",
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow Wix site origins to call this API from the browser.
# ALLOWED_ORIGINS env var is a comma-separated list of allowed origins.
# Defaults to Wix editor preview + production pattern. Tighten in production.
# ---------------------------------------------------------------------------
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    ",".join([
        "https://www.detroitfamilyhomecare.com",
        "https://detroitfamilyhomecare.com",
        "https://editor.wix.com",
        "https://create.editorx.com"
    ])
)
)
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

# Routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(clients.router, prefix="/clients", tags=["clients"])


@app.get("/health", tags=["health"])
def health() -> dict:
    """Public health check — no auth, no DB. Safe to call from Wix backend."""
    return {"status": "ok", "service": "dfhc-api", "version": "0.1.0"}
