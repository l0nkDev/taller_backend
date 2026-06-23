from typing import Optional

from pydantic import BaseModel


class DishCreate(BaseModel):
    name: str
    description: str
    category_id: int
    price: float
    cost: float
    available: bool


class DishRead(BaseModel):
    id: int
    name: str
    description: str
    category_id: int
    price: float
    cost: Optional[float] = None
    available: bool
    category_name: Optional[str] = None


class DishReadFlat(BaseModel):
    id: int
    name: str
    description: str
    price: float
    cost: Optional[float] = None
    available: bool


class DishUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    available: Optional[bool] = None
