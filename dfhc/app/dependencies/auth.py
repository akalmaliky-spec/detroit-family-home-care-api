from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dfhc.app.core.database import get_db
from dfhc.app.core.security import decode_access_token
from dfhc.app.repositories.users import get_user_by_id
from dfhc.app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    try:
        user_id = int(payload["sub"]) if payload else None
    except (TypeError, ValueError, KeyError):
        user_id = None
    user = get_user_by_id(db, user_id) if user_id is not None else None
    if not user or not user.is_active or payload["ver"] != user.token_version:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return user
