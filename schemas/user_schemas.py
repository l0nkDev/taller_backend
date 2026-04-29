from typing import Optional

from pydantic import BaseModel

from models.user import UserRole


class UserCreate(BaseModel):
    username: str
    password: str
    fname: str
    lname: str
    phone: str
    role: Optional[UserRole] = UserRole.WAITER


class UserRead(BaseModel):
    id: int
    username: str
    fname: str
    lname: str
    phone: str
    role: UserRole
    is_active: bool


class UserUpdate(BaseModel):
    password: Optional[str] = None
    fname: Optional[str] = None
    lname: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
