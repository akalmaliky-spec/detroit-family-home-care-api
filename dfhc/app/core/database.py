import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ---------------------------------------------------------------------------
# DATABASE_URL — required in all environments.
# In CI/testing, set TESTING=true and DATABASE_URL to sqlite:///./test.db
# or any valid URL. In production this MUST be a PostgreSQL URL.
# No SQLite fallback is provided here to prevent silent data loss on
# platforms (Render, Railway) that wipe the local filesystem on redeploy.
# ---------------------------------------------------------------------------
_TESTING = os.getenv("TESTING", "").lower() in ("1", "true", "yes")

if _TESTING:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
else:
    DATABASE_URL = os.environ["DATABASE_URL"]  # raises KeyError if unset in production

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
