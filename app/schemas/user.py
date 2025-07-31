from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.models.user import UserType


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    user_type: UserType
    phone_number: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserInDB):
    pass


# Authentication schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
