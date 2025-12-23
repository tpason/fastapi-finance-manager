from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.models.enums import UserRole
from decimal import Decimal


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    limit_amount: Optional[Decimal] = 2000000.0


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.MEMBER


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    limit_amount: Optional[Decimal] = None


class UserInDB(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    role: UserRole = UserRole.MEMBER
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    pass

