from pydantic import BaseModel

from schemas.order_detail_schemas import OrderDetailRead


class OrderRead(BaseModel):
    id: int
    tablegroup_id: int
    was_paid: bool
    was_cancelled: bool
    detail: list[OrderDetailRead] = []
