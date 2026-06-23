from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional


class DishCost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cost: float = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)

    dish_id: int = Field(foreign_key="dish.id")

    dish: "Dish" = Relationship(back_populates="costs")
