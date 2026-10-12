from datetime import datetime, timezone
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dfhc.app.core.database import get_db
from dfhc.app.core.security import verify_password, get_password_hash, refresh_token_hash
from dfhc.app.core.sessions import issue_tokens, revoke_user_sessions
from dfhc.app.core.rate_limit import auth_rate_limiter
from dfhc.app.dependencies.auth import get_current_user
from dfhc.app.models import RefreshSession, User
from dfhc.app.schemas import Token, RefreshRequest

router = APIRouter()
_DUMMY_HASH = get_password_hash(secrets.token_urlsafe(32))


def unauthorized():
    return HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})


def no_store(response: Response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


@router.post('/token', response_model=Token)
def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_rate_limiter.check(request)
    user = db.query(User).filter(User.email == form_data.username).with_for_update().first()
    valid = verify_password(form_data.password, user.hashed_password if user else _DUMMY_HASH)
    if not user or not valid or not user.is_active:
        raise unauthorized()
    no_store(response)
    return issue_tokens(db, user)


@router.post('/refresh', response_model=Token)
def refresh(body: RefreshRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    auth_rate_limiter.check(request)
    token_hash = refresh_token_hash(body.refresh_token)
    existing = db.get(RefreshSession, token_hash)
    if existing is None:
        raise unauthorized()
    # Lock the user before the session, matching password-reset/logout lock order.
    user = db.query(User).filter(User.id == existing.user_id).populate_existing().with_for_update().first()
    session = db.query(RefreshSession).filter(RefreshSession.token_hash == token_hash).populate_existing().with_for_update().first()
    now = datetime.now(timezone.utc)
    expiry = session.expires_at.replace(tzinfo=timezone.utc) if session and session.expires_at.tzinfo is None else (session.expires_at if session else now)
    if not session or session.revoked or expiry <= now or not user or not user.is_active:
        raise unauthorized()
    session.revoked = True
    no_store(response)
    return issue_tokens(db, user)


@router.post('/logout', status_code=204)
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).populate_existing().with_for_update().one()
    revoke_user_sessions(db, user)
    db.commit()
