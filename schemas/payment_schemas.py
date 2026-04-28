from typing import Optional

from pydantic import BaseModel
from models.order_detail import DetailStatus
from models.payment import PaymentMethod
from schemas.order_schemas import OrderRead

class PaymentCreate(BaseModel):
    method: PaymentMethod

class PaymentRead(BaseModel):
    id: int
    method: PaymentMethod
    total: float
    order: OrderRead

