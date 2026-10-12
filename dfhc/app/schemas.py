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

def validate_password(value: str) -> str:
    if not MIN_PASSWORD_LEN <= len(value) <= MAX_PASSWORD_LEN:
        raise ValueError(f"Password must be {MIN_PASSWORD_LEN}-{MAX_PASSWORD_LEN} characters")
    if len(value.encode("utf-8")) > MAX_BCRYPT_BYTES:
        raise ValueError(f"Password exceeds {MAX_BCRYPT_BYTES} UTF-8 bytes (bcrypt limit)")
    return value


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_policy(cls, value: str) -> str:
        return validate_password(value)


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("password")
    @classmethod
    def password_policy(cls, value: Optional[str]) -> str:
        if value is None:
            raise ValueError("Password cannot be null")
        return validate_password(value)


class SelfUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_policy(cls, value: Optional[str]) -> str:
        if value is None:
            raise ValueError("Password cannot be null")
        return validate_password(value)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_superuser: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str


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
    owner_user_id: Optional[int] = None


class ClientUpdate(BaseModel):
    owner_user_id: Optional[int] = None
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
