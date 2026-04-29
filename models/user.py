from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    WAITER = "waiter"
    KITCHEN = "kitchen"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    fname: str = Field()
    lname: str = Field()
    phone: str = Field()
    hashed_password: str
    role: UserRole = Field(default=UserRole.WAITER)
    is_active: bool = Field(default=True)
