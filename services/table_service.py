from sqlmodel import Session
from models.table import Table
from models.table_group import TableGroup
from schemas.table_schemas import TableCreate


def create_new_table(session: Session, table_data: TableCreate) -> Table:
    default_group = TableGroup(
        floor_id=table_data.floor_id, capacity=table_data.capacity
    )
    session.add(default_group)
    session.flush()
    active_group_id = table_data.current_group_id or default_group.id
    db_table = Table(
        pos_x=table_data.pos_x,
        pos_y=table_data.pos_y,
        width=table_data.width,
        height=table_data.height,
        rotation=table_data.rotation,
        base_group_id=default_group.id,
        current_group_id=active_group_id,
    )
    session.add(db_table)
    session.commit()
    session.refresh(db_table)
    return db_table
