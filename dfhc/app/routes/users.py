from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dfhc.app.core.database import get_db
from dfhc.app.dependencies.auth import get_current_superuser, get_current_user
from dfhc.app.repositories import users as user_repo
from dfhc.app.schemas import UserCreate, UserOut, UserUpdate

# User management is admin-only. The first admin is created from the command
# line with: python -m dfhc.scripts.create_admin <email>
router = APIRouter()


@router.get("/me", response_model=UserOut)
def read_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_superuser),
):
    existing = user_repo.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_repo.create_user(db, user_in)


@router.get("/", response_model=List[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin=Depends(get_current_superuser),
):
    return user_repo.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_superuser)):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_superuser),
):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_in.email and user_in.email != user.email and user_repo.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_repo.update_user(db, user, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_superuser)):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot delete their own account")
    user_repo.delete_user(db, user_id)
