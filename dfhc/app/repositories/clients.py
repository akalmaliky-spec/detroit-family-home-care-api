from typing import List, Optional
from sqlalchemy.orm import Session
from dfhc.app.models import Client
from dfhc.app.schemas import ClientCreate, ClientUpdate


def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    return db.query(Client).offset(skip).limit(limit).all()


def get_client(db: Session, client_id: int) -> Optional[Client]:
    return db.query(Client).filter(Client.id == client_id).first()


def create_client(db: Session, client_in: ClientCreate) -> Client:
    client = Client(**client_in.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update_client(
    db: Session, client_id: int, client_in: ClientUpdate
) -> Optional[Client]:
    client = get_client(db, client_id)
    if not client:
        return None
    for field, value in client_in.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: int) -> Optional[Client]:
    client = get_client(db, client_id)
    if not client:
        return None
    db.delete(client)
    db.commit()
    return client
