from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    was_paid: bool = Field(default=False)
    was_cancelled: bool = Field(default=False)
    tablegroup_id: int = Field(foreign_key="tablegroup.id")

    detail: List["OrderDetail"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"order_by": "OrderDetail.id"},
    )
    payment: Optional["Payment"] = Relationship(back_populates="order")
    tablegroup: "TableGroup" = Relationship()
