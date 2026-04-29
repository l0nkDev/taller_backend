from typing import Optional

from pydantic import BaseModel

from schemas.table_group_schemas import TableGroupRead


class FloorCreate(BaseModel):
    name: str


class FloorRead(BaseModel):
    id: int
    name: str
    table_groups: list[TableGroupRead] = []


class FloorUpdate(BaseModel):
    name: Optional[str] = None
