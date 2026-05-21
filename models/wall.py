from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Wall(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    floor_id: int = Field(foreign_key="floor.id")
    x1: float
    y1: float
    x2: float
    y2: float
    isDoor: bool = Field(default=False)


    floor: "Floor" = Relationship(back_populates="walls")