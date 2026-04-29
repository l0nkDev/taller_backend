from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class Dish(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    description: str = Field()
    category_id: int = Field(foreign_key="category.id")
    available: bool = Field()

    prices: List["DishPrice"] = Relationship(back_populates="dish")
    category: "Category" = Relationship(back_populates="dishes")

    @property
    def price(self) -> float | None:
        active = next((p for p in self.prices if p.is_active), None)
        return active.price if active else None

    @property
    def category_name(self) -> str | None:
        return self.category.name if self.category else None
