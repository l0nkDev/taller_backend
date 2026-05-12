from typing import Optional

from pydantic import BaseModel


class TableCreate(BaseModel):
    offset_x: float
    offset_y: float
    width: float
    height: float
    rotation: float
    capacity: int
    floor_id: int
    current_group_id: Optional[int] = None


class TableRead(BaseModel):
    id: int
    offset_x: float
    offset_y: float
    width: float
    height: float
    rotation: float
    base_group_id: int
    current_group_id: int


class TableUpdate(BaseModel):
    offset_x: Optional[float] = None
    offset_y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    rotation: Optional[float] = None
    current_group_id: Optional[int] = None
