import asyncio
import json
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from database import get_session
from models.table_group import TableGroup
from models.user import User
from schemas.floor_schemas import FloorRead
from schemas.table_group_schemas import (
    TableGroupCreate,
    TableGroupRead,
    TableGroupUpdate,
)
from schemas.table_schemas import TableCreate, TableRead, TableUpdate
from schemas.wall_schemas import WallCreate, WallRead, WallUpdate
from fastapi.encoders import jsonable_encoder
from core.security import require_any, require_admin
from services import floor_service, table_service, wall_service

router = APIRouter(prefix="/editor", tags=["Editor"])

connected_clients = {}


async def event_generator(request: Request, floor_id: int):
    client_queue = asyncio.Queue()
    if floor_id not in connected_clients:
        connected_clients[floor_id] = []
    connected_clients[floor_id].append(client_queue)
    try:
        while True:
            if await request.is_disconnected():
                break
            try:
                data = await asyncio.wait_for(client_queue.get(), timeout=2.0)
                yield f"data: {data}\n\n"
            except asyncio.TimeoutError:
                continue
    finally:
        connected_clients[floor_id].remove(client_queue)
        if not connected_clients[floor_id]:
            del connected_clients[floor_id]


@router.get("/floor/{floor_id}/stream")
async def sse_floor_updates(request: Request, floor_id: int):
    return StreamingResponse(
        event_generator(request, floor_id), media_type="text/event-stream"
    )


@router.get("/floor/{floor_id}", response_model=FloorRead)
def read_floor_endpoint(
    floor_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_any),
):
    floor = floor_service.get_floor_by_id(session=session, floor_id=floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return floor


@router.post("/tables")
async def create_table(
    payload: TableCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    new_table = table_service.create_new_table(
        session=session, table_data=payload
    )
    table_read = TableRead.model_validate(new_table, from_attributes=True)
    ctg_read = TableGroupRead.model_validate(
        new_table.current_group, from_attributes=True
    )
    btg_read = TableGroupRead.model_validate(
        new_table.base_group, from_attributes=True
    )
    event_data = json.dumps(
        {
            "action": "create_table",
            "table": jsonable_encoder(table_read),
            "current_group": jsonable_encoder(ctg_read),
            "base_group": jsonable_encoder(btg_read),
        }
    )
    floor_id = ctg_read.floor_id
    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Mesa creada exitosamente", "data": table_read}


@router.patch("/tables/{table_id}")
async def update_table(
    payload: TableUpdate,
    table_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    new_table = table_service.update_table(
        session=session, table_id=table_id, table_data=payload
    )
    ctg_read = TableGroupRead.model_validate(
        new_table.current_group, from_attributes=True
    )
    btg_read = TableGroupRead.model_validate(
        new_table.base_group, from_attributes=True
    )
    table_read = TableRead.model_validate(new_table, from_attributes=True)
    event_data = json.dumps(
        {
            "action": "update_table",
            "table": jsonable_encoder(table_read),
            "current_group": jsonable_encoder(ctg_read),
            "base_group": jsonable_encoder(btg_read),
        }
    )
    floor_id = ctg_read.floor_id
    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {
        "message": "Mesa actualizada exitosamente",
        "data": table_read,
    }


@router.post("/tablegroups")
async def create_group(
    payload: TableGroupCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    new_table = table_service.group_tables(session=session, table_data=payload)
    table_read = TableGroupRead.model_validate(new_table, from_attributes=True)
    event_data = json.dumps(
        {"action": "create_group", "tablegroup": jsonable_encoder(table_read)}
    )
    floor_id = new_table.floor_id

    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Grupo creado exitosamente", "data": table_read}


@router.patch("/tablegroups/{tablegroup_id}")
async def update_group(
    payload: TableGroupUpdate,
    tablegroup_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    new_table = table_service.update_tablegroup(
        session=session, group_id=tablegroup_id, group_data=payload
    )
    table_read = TableGroupRead.model_validate(new_table, from_attributes=True)
    event_data = json.dumps(
        {"action": "update_group", "tablegroup": jsonable_encoder(table_read)}
    )
    floor_id = new_table.floor_id
    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Grupo actualizado exitosamente", "data": table_read}


@router.post("/tablegroups/{tablegroup_id}/disband")
async def disband_group(
    tablegroup_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    group = session.get(TableGroup, tablegroup_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")

    floor_id = group.floor_id
    table_service.disband_tablegroup(session, tablegroup_id)
    if floor_id in connected_clients:
        event_data = json.dumps({"action": "refresh_floor"})
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Grupo desarmado exitosamente"}


@router.post("/walls")
async def create_wall(
    payload: WallCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    new_wall = wall_service.create_new_wall(session=session, wall_data=payload)
    wall_read = WallRead.model_validate(new_wall, from_attributes=True)
    event_data = json.dumps(
        {"action": "create_wall", "wall": jsonable_encoder(wall_read)}
    )

    floor_id = payload.floor_id
    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Pared creada", "data": wall_read}


@router.patch("/walls/{wall_id}")
async def update_wall(
    payload: WallUpdate,
    wall_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    updated_wall = wall_service.update_wall(
        session=session, wall_id=wall_id, wall_data=payload
    )
    if not updated_wall:
        raise HTTPException(status_code=404, detail="Pared no encontrada")

    wall_read = WallRead.model_validate(updated_wall, from_attributes=True)
    event_data = json.dumps(
        {"action": "update_wall", "wall": jsonable_encoder(wall_read)}
    )

    floor_id = updated_wall.floor_id
    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Pared actualizada", "data": wall_read}


@router.delete("/walls/{wall_id}")
async def delete_wall(
    wall_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    from models.wall import Wall

    db_wall = session.get(Wall, wall_id)
    if not db_wall:
        raise HTTPException(status_code=404, detail="Pared no encontrada")

    floor_id = db_wall.floor_id
    wall_service.delete_wall(session, wall_id)

    if floor_id in connected_clients:
        event_data = json.dumps({"action": "delete_wall", "wall_id": wall_id})
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Pared eliminada"}
