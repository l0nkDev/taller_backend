from typing import Optional

from pydantic import BaseModel
from models.order_detail import DetailStatus

class OrderDetailCreate(BaseModel):
    dish_id: int
    quantity: int
    tablegroup_id: Optional[int]
    discount: float
    status: DetailStatus

class OrderDetailRead(BaseModel):
    id: int
    dish_id: int
    dish_name: str
    quantity: int
    order_id: int
    discount: float
    status: DetailStatus

class OrderDetailUpdate(BaseModel):
    dish_id: Optional[int] = None
    quantity: Optional[int] = None
    discount: Optional[float] = None
    status: Optional[DetailStatus] = None
