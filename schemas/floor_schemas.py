from typing import Optional

from pydantic import BaseModel

from schemas.table_group_schemas import TableGroupRead
from schemas.wall_schemas import WallRead


class FloorCreate(BaseModel):
    name: str


class FloorRead(BaseModel):
    id: int
    name: str
    table_groups: list[TableGroupRead] = []
    walls: list[WallRead] = []


class FloorUpdate(BaseModel):
    name: Optional[str] = None
