from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dfhc.app.core.database import get_db
from dfhc.app.schemas import ClientCreate, ClientOut, ClientUpdate
from dfhc.app.repositories import clients as client_repo

router = APIRouter()


@router.get('/', response_model=List[ClientOut])
def list_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return client_repo.get_clients(db, skip=skip, limit=limit)


@router.get('/{client_id}', response_model=ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = client_repo.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail='Client not found')
    return client


@router.post('/', response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(client_in: ClientCreate, db: Session = Depends(get_db)):
    return client_repo.create_client(db, client_in)


@router.patch('/{client_id}', response_model=ClientOut)
def update_client(client_id: int, client_in: ClientUpdate, db: Session = Depends(get_db)):
    client = client_repo.update_client(db, client_id, client_in)
    if not client:
        raise HTTPException(status_code=404, detail='Client not found')
    return client


@router.delete('/{client_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = client_repo.delete_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail='Client not found')
