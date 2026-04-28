from typing import Optional

from pydantic import BaseModel

from schemas.table_schemas import TableRead

class TableGroupCreate(BaseModel):
    floor_id: int
    capacity: int
    is_active: Optional[bool] = True

class TableGroupRead(BaseModel):
    id: int
    floor_id: int
    capacity: int
    is_active: bool
    current_tables: list[TableRead] = []
    
class TableGroupUpdate(BaseModel):
    capacity: Optional[int] = None
    is_active: Optional[bool] = None
    
    