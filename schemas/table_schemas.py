from typing import Optional

from pydantic import BaseModel

class TableCreate(BaseModel):
    pos_x: float
    pos_y: float
    width: float
    height: float
    rotation: float
    capacity: int
    floor_id: int
    current_group_id: Optional[int] = None

class TableRead(BaseModel):
    id: int
    pos_x: float
    pos_y: float
    width: float
    height: float
    rotation: float
    base_group_id: int
    current_group_id: int

class TableUpdate(BaseModel):
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    rotation: Optional[float] = None
    current_group_id: Optional[int] = None
