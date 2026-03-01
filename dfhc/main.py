import os
from fastapi import FastAPI
from dfhc.app.core.database import engine, Base
from dfhc.app.routes import users, auth

_WEAK_SECRETS = {
    "dev-secret-key-change-in-prod",
    "dev-secret-key-change-in-production",
    "changeme",
    "secret",
    "insecure",
}

def _check_secret_key() -> None:
    testing = os.getenv("TESTING", "").lower() in ("1", "true", "yes")
    if testing:
        return
    secret = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
    if secret in _WEAK_SECRETS or len(secret) < 32:
        raise RuntimeError(
            "SECRET_KEY is weak or default. "
            "Set a strong SECRET_KEY env var before running in production. "
            "Minimum 32 characters required."
        )

Base.metadata.create_all(bind=engine)
_check_secret_key()

app = FastAPI(title="DFHC API", version="0.1.0")
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "dfhc-api"}
