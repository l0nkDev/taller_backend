from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional


class PaymentMethod(str, Enum):
    CASH = "C"
    QR = "Q"


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    method: PaymentMethod = Field()
    total: float
    created_at: datetime = Field(default_factory=datetime.now)
    order_id: int = Field(foreign_key="order.id")

    order: "Order" = Relationship(back_populates="payment")
