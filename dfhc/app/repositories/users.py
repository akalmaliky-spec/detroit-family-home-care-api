from typing import Optional
from sqlalchemy.orm import Session
from dfhc.app.models import User, Client, RefreshSession
from dfhc.app.core.sessions import revoke_user_sessions
from dfhc.app.schemas import UserCreate, UserUpdate
from dfhc.app.core.security import get_password_hash


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    db_user = db.query(User).filter(User.id == db_user.id).populate_existing().with_for_update().one()
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data or "is_active" in update_data:
        revoke_user_sessions(db, db_user)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.query(RefreshSession).filter(RefreshSession.user_id == user_id).delete()
        db.query(Client).filter(Client.owner_user_id == user_id).update({"owner_user_id": None})
        db.delete(db_user)
        db.commit()
    return db_user
