from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class TableGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pos_x: float
    pos_y: float
    rotation: float
    capacity: int
    is_active: bool = Field(default=True)

    floor_id: int = Field(foreign_key="floor.id")

    base_table: "Table" = Relationship(
        back_populates="base_group",
        sa_relationship_kwargs={
            "uselist": False,
            "primaryjoin": "TableGroup.id == Table.base_group_id",
        },
    )
    current_tables: List["Table"] = Relationship(
        back_populates="current_group",
        sa_relationship_kwargs={
            "primaryjoin": "TableGroup.id == Table.current_group_id"
        },
    )
    floor: "Floor" = Relationship(back_populates="table_groups")
