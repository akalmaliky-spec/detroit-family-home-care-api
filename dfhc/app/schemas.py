from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime, date

MIN_PASSWORD_LEN = 10
MAX_PASSWORD_LEN = 256
MAX_BCRYPT_BYTES = 72

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < MIN_PASSWORD_LEN:
            raise ValueError(f"Password must be at least {MIN_PASSWORD_LEN} characters")
        if len(v) > MAX_PASSWORD_LEN:
            raise ValueError(f"Password must not exceed {MAX_PASSWORD_LEN} characters")
        if len(v.encode("utf-8")) > MAX_BCRYPT_BYTES:
            raise ValueError(
                f"Password exceeds {MAX_BCRYPT_BYTES} UTF-8 bytes (bcrypt limit). "
                "Use a shorter password or ASCII-only characters."
            )
        return v

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_superuser: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None


class ClientBase(BaseModel):
    full_name: str
    date_of_birth: Optional[date] = None
    diagnosis: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medicaid_id: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    diagnosis: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medicaid_id: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class ClientOut(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
