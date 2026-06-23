import math

from sqlmodel import Session, select
from models.table import Table
from models.table_group import TableGroup
from schemas.table_group_schemas import TableGroupCreate, TableGroupUpdate
from schemas.table_schemas import TableCreate, TableUpdate


def create_new_table(session: Session, table_data: TableCreate) -> Table:
    default_group = TableGroup(
        floor_id=table_data.floor_id,
        capacity=table_data.capacity,
        pos_x=0.0,
        pos_y=0.0,
        rotation=0.0,
    )
    session.add(default_group)
    session.flush()

    active_group_id = table_data.current_group_id or default_group.id
    is_independent = active_group_id == default_group.id

    if is_independent:
        default_group.pos_x = table_data.offset_x
        default_group.pos_y = table_data.offset_y
        default_group.rotation = table_data.rotation
        table_offset_x = 0.0
        table_offset_y = 0.0
        table_rot = 0.0
    else:
        default_group.pos_x = 0.0
        default_group.pos_y = 0.0
        default_group.rotation = 0.0
        table_offset_x = table_data.offset_x
        table_offset_y = table_data.offset_y
        table_rot = table_data.rotation

    db_table = Table(
        width=table_data.width,
        height=table_data.height,
        base_group_id=default_group.id,
        current_group_id=active_group_id,
        offset_x=table_offset_x,
        offset_y=table_offset_y,
        rotation=table_rot,
    )

    session.add(db_table)
    session.commit()
    session.refresh(db_table)
    return db_table


def update_table(
    session: Session, table_id: int, table_data: TableUpdate
) -> Table:
    db_table = session.get(Table, table_id)
    if not db_table:
        return None

    if table_data.current_group_id is not None:
        db_table.current_group_id = table_data.current_group_id

    is_independent = db_table.current_group_id == db_table.base_group_id

    if is_independent:
        base_group = session.get(TableGroup, db_table.base_group_id)

        if table_data.offset_x is not None:
            base_group.pos_x = table_data.offset_x
        if table_data.offset_y is not None:
            base_group.pos_y = table_data.offset_y
        if table_data.rotation is not None:
            base_group.rotation = table_data.rotation

        db_table.offset_x = 0.0
        db_table.offset_y = 0.0
        db_table.rotation = 0.0

        session.add(base_group)
    else:
        if table_data.offset_x is not None:
            db_table.offset_x = table_data.offset_x
        if table_data.offset_y is not None:
            db_table.offset_y = table_data.offset_y
        if table_data.rotation is not None:
            db_table.rotation = table_data.rotation

    if table_data.width is not None:
        db_table.width = table_data.width
    if table_data.height is not None:
        db_table.height = table_data.height

    session.add(db_table)
    session.commit()
    session.refresh(db_table)
    return db_table


def update_tablegroup(
    session: Session, group_id: int, group_data: TableGroupUpdate
) -> TableGroup:
    db_group = session.get(TableGroup, group_id)
    if not db_group:
        return None

    if group_data.pos_x is not None:
        db_group.pos_x = group_data.pos_x
    if group_data.pos_y is not None:
        db_group.pos_y = group_data.pos_y
    if group_data.rotation is not None:
        db_group.rotation = group_data.rotation
    if group_data.capacity is not None:
        db_group.capacity = group_data.capacity

    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return db_group


def group_tables(session: Session, table_data: TableGroupCreate) -> TableGroup:
    tables = session.exec(
        select(Table).where(Table.id.in_(table_data.table_ids))
    ).all()

    new_group = TableGroup(
        pos_x=table_data.pos_x,
        pos_y=table_data.pos_y,
        rotation=table_data.rotation,
        capacity=table_data.capacity,
        floor_id=table_data.floor_id,
    )
    session.add(new_group)
    session.flush()

    # Pre-calculamos la rotación inversa del nuevo grupo para la fórmula de conversión
    new_rad = math.radians(-new_group.rotation)
    cos_n = math.cos(new_rad)
    sin_n = math.sin(new_rad)

    for table in tables:
        # 1. Descubrir la posición GLOBAL (física real) de la mesa antes de moverla
        curr_group = session.get(TableGroup, table.current_group_id)

        rad = math.radians(curr_group.rotation)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)

        global_x = curr_group.pos_x + (
            table.offset_x * cos_r - table.offset_y * sin_r
        )
        global_y = curr_group.pos_y + (
            table.offset_x * sin_r + table.offset_y * cos_r
        )
        global_rot = curr_group.rotation + table.rotation

        # 2. Calculamos la distancia desde el nuevo grupo central hacia la mesa
        dx = global_x - new_group.pos_x
        dy = global_y - new_group.pos_y

        # 3. Aplicamos rotación inversa para que el offset sea relativo al nuevo eje rotado
        table.offset_x = dx * cos_n - dy * sin_n
        table.offset_y = dx * sin_n + dy * cos_n
        table.rotation = global_rot - new_group.rotation

        table.current_group_id = new_group.id
        session.add(table)

    session.commit()
    session.refresh(new_group)
    return new_group


def disband_tablegroup(session: Session, group_id: int):
    complex_group = session.get(TableGroup, group_id)
    if not complex_group:
        return

    tables_in_group = session.exec(
        select(Table).where(Table.current_group_id == group_id)
    ).all()

    rad = math.radians(complex_group.rotation)
    cos_rot = math.cos(rad)
    sin_rot = math.sin(rad)

    for table in tables_in_group:
        base_group = session.get(TableGroup, table.base_group_id)

        # 1. Recuperamos la posición global real aplicando la rotación del grupo complejo
        global_x = complex_group.pos_x + (
            table.offset_x * cos_rot - table.offset_y * sin_rot
        )
        global_y = complex_group.pos_y + (
            table.offset_x * sin_rot + table.offset_y * cos_rot
        )
        global_rot = complex_group.rotation + table.rotation

        # 2. Obligamos al grupo base a materializarse exactamente en esa coordenada global
        base_group.pos_x = global_x
        base_group.pos_y = global_y
        base_group.rotation = global_rot

        # 3. Soltamos la mesa, su offset vuelve a ser 0,0 (puro)
        table.current_group_id = table.base_group_id
        table.offset_x = 0.0
        table.offset_y = 0.0
        table.rotation = 0.0

        session.add(base_group)
        session.add(table)

    # FIX DEL SOFT DELETE: Solo desactivamos el grupo complejo si estamos 100%
    # seguros de que NO ES el grupo base de ninguna mesa (limpieza de datos sucios legacy).
    is_base = session.exec(
        select(Table).where(Table.base_group_id == complex_group.id)
    ).first()
    if not is_base:
        complex_group.is_active = False
        session.add(complex_group)

    session.commit()
