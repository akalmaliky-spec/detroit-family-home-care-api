from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone

from dfhc.app.core.database import Base


def _utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime.

    Replaces the deprecated datetime.utcnow() which SQLAlchemy will remove
    in a future version. Using datetime.now(UTC) returns a tz-aware object.
    """
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
