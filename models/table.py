from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class Table(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    offset_x: float
    offset_y: float
    width: float
    height: float
    rotation: float

    base_group_id: int = Field(foreign_key="tablegroup.id")
    current_group_id: int = Field(foreign_key="tablegroup.id")

    base_group: "TableGroup" = Relationship(
        back_populates="base_table",
        sa_relationship_kwargs={"foreign_keys": "[Table.base_group_id]"},
    )
    current_group: "TableGroup" = Relationship(
        back_populates="current_tables",
        sa_relationship_kwargs={"foreign_keys": "[Table.current_group_id]"},
    )
