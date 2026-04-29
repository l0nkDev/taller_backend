from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()

    dishes: List["Dish"] = Relationship(back_populates="category")
