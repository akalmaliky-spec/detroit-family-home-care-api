from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy.orm import Session
from dfhc.app.models import RefreshSession, User
from dfhc.app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from dfhc.app.core.security import create_access_token, refresh_token_hash


def revoke_user_sessions(db: Session, user: User) -> None:
    user.token_version += 1
    db.query(RefreshSession).filter(RefreshSession.user_id == user.id).update({"revoked": True})


def issue_tokens(db: Session, user: User) -> dict:
    refresh_token = secrets.token_urlsafe(48)
    db.add(RefreshSession(
        token_hash=refresh_token_hash(refresh_token),
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    access_token = create_access_token({"sub": str(user.id), "ver": user.token_version})
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}
