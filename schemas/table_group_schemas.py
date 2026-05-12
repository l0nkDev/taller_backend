from typing import Optional

from pydantic import BaseModel

from schemas.table_schemas import TableRead


class TableGroupCreate(BaseModel):
    pos_x: float
    pos_y: float
    rotation: float
    floor_id: int
    capacity: int
    is_active: Optional[bool] = True
    table_ids: list[int]


class TableGroupRead(BaseModel):
    id: int
    pos_x: float
    pos_y: float
    rotation: float
    floor_id: int
    capacity: int
    is_active: bool
    current_tables: list[TableRead] = []


class TableGroupUpdate(BaseModel):
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    rotation: Optional[float] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None
