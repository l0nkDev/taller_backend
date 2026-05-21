from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class Floor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    walls: List["Wall"] = Relationship(back_populates="floor")
    table_groups: List["TableGroup"] = Relationship(back_populates="floor")
