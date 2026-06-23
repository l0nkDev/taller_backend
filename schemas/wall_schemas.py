from typing import Optional
from pydantic import BaseModel


class WallCreate(BaseModel):
    floor_id: int
    x1: float
    y1: float
    x2: float
    y2: float
    isDoor: Optional[bool] = False


class WallUpdate(BaseModel):
    x1: Optional[float] = None
    y1: Optional[float] = None
    x2: Optional[float] = None
    y2: Optional[float] = None
    isDoor: Optional[bool] = None


class WallRead(BaseModel):
    id: int
    floor_id: int
    x1: float
    y1: float
    x2: float
    y2: float
    isDoor: bool
