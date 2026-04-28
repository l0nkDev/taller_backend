from enum import Enum

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class DetailStatus(str, Enum):
    TAKEN = "T"
    IN_KITCHEN = "K"
    COOKING = "C"
    READY = "R"
    SERVED = "S"
    CANCELLED = "X"

class OrderDetail(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field()
    discount: float = Field()
    status: DetailStatus = Field()

    order_id: int = Field(foreign_key="order.id")
    price_id: int = Field(foreign_key="dishprice.id")

    order: "Order" = Relationship(back_populates="detail")
    price: "DishPrice" = Relationship()

    @property
    def dish_id(self) -> int | None:
        return self.price.dish_id if self.price else None
    @property
    def dish_name(self) -> str | None:
        return self.price.dish.name if self.price and self.price.dish else None