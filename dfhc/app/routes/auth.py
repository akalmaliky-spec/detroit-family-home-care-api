from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dfhc.app.core.database import get_db
from dfhc.app.core.security import verify_password, create_access_token
from dfhc.app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from dfhc.app.repositories import users as user_repo
from dfhc.app.schemas import Token

router = APIRouter()

@router.post('/token', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_repo.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    token = create_access_token(
        data={'sub': user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {'access_token': token, 'token_type': 'bearer'}
