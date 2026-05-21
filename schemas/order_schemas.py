from pydantic import BaseModel

from models.order_detail import DetailStatus
from schemas.order_detail_schemas import OrderDetailRead


class OrderRead(BaseModel):
    id: int
    tablegroup_id: int
    was_paid: bool
    was_cancelled: bool
    detail: list[OrderDetailRead] = []

class OrderItemCreate(BaseModel):
    dish_id: int
    quantity: int
    discount: float = 0.0
    status: DetailStatus = DetailStatus.TAKEN

class OrderBulkSync(BaseModel):
    tablegroup_id: int
    items: list[OrderItemCreate]