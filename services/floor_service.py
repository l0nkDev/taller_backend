from sqlmodel import Session, select
from models.floor import Floor
from sqlalchemy.orm import selectinload
from models.table_group import TableGroup
from schemas.floor_schemas import FloorCreate


def create_new_floor(session: Session, floor_data: FloorCreate) -> Floor:
    db_floor = Floor(name=floor_data.name)
    session.add(db_floor)
    session.commit()
    session.refresh(db_floor)
    return db_floor


def get_floor_by_id(session: Session, floor_id: int) -> Floor | None:
    statement = (
        select(Floor)
        .where(Floor.id == floor_id)
        .options(
            selectinload(Floor.table_groups.and_(TableGroup.is_active is True))
        )
    )
    return session.exec(statement).first()


def get_all_floors(session: Session) -> list[Floor]:
    statement = select(Floor).options(
        selectinload(Floor.table_groups.and_(TableGroup.is_active is True))
    )
    return session.exec(statement).all()
