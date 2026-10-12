from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dfhc.app.core.database import get_db
from dfhc.app.dependencies.auth import get_current_user, require_admin
from dfhc.app.models import User
from dfhc.app.schemas import UserCreate, UserOut, UserUpdate, SelfUpdate
from dfhc.app.repositories import users as user_repo

router = APIRouter()


@router.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_repo.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail='Email already registered')
    return user_repo.create_user(db, user_in)


@router.get('/me', response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.patch('/me', response_model=UserOut)
def update_me(body: SelfUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_repo.update_user(db, user, UserUpdate(**body.model_dump(exclude_unset=True)))


@router.get('/', response_model=List[UserOut], dependencies=[Depends(require_admin)])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_repo.get_users(db, skip=skip, limit=limit)


@router.get('/{user_id}', response_model=UserOut, dependencies=[Depends(require_admin)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@router.patch('/{user_id}', response_model=UserOut, dependencies=[Depends(require_admin)])
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user_in.email and user_in.email != user.email and user_repo.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail='Email already registered')
    if any(value is None for key, value in user_in.model_dump(exclude_unset=True).items() if key in ('email', 'is_active')):
        raise HTTPException(status_code=422, detail='Email and active status cannot be null')
    return user_repo.update_user(db, user, user_in)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if not user_repo.get_user_by_id(db, user_id):
        raise HTTPException(status_code=404, detail='User not found')
    user_repo.delete_user(db, user_id)
