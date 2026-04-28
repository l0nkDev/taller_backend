from typing import Optional

from pydantic import BaseModel

from schemas.dish_schemas import DishReadFlat

class CategoryCreate(BaseModel):
    name: str

class CategoryRead(BaseModel):
    id: int
    name: str
    dishes: list[DishReadFlat] = []

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
