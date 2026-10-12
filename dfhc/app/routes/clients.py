from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dfhc.app.core.database import get_db
from dfhc.app.dependencies.auth import get_current_user, require_admin
from dfhc.app.models import Client, User
from dfhc.app.schemas import ClientCreate, ClientOut, ClientUpdate
from dfhc.app.repositories import clients as client_repo

router = APIRouter()


def accessible_client(db: Session, client_id: int, user: User):
    query = db.query(Client).filter(Client.id == client_id)
    if not user.is_superuser:
        query = query.filter(Client.owner_user_id == user.id)
    client = query.first()
    if not client:
        raise HTTPException(status_code=404, detail='Client not found')
    return client


def validate_owner(db: Session, owner_id):
    if owner_id is not None and not db.query(User).filter(User.id == owner_id, User.is_active.is_(True)).first():
        raise HTTPException(status_code=422, detail='Owner must be an active user')


@router.get('/', response_model=List[ClientOut])
def list_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(Client)
    if not user.is_superuser:
        query = query.filter(Client.owner_user_id == user.id)
    return query.offset(skip).limit(limit).all()


@router.get('/{client_id}', response_model=ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return accessible_client(db, client_id, user)


@router.post('/', response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(body: ClientCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    validate_owner(db, body.owner_user_id)
    return client_repo.create_client(db, body)


@router.patch('/{client_id}', response_model=ClientOut)
def update_client(client_id: int, body: ClientUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    accessible_client(db, client_id, user)
    if 'owner_user_id' in body.model_fields_set:
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail='Only administrators can assign owners')
        validate_owner(db, body.owner_user_id)
    return client_repo.update_client(db, client_id, body)


@router.delete('/{client_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    accessible_client(db, client_id, user)
    client_repo.delete_client(db, client_id)
