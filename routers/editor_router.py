import asyncio
import json
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from database import get_session
from models.user import User
from schemas.floor_schemas import FloorRead
from schemas.table_group_schemas import TableGroupCreate, TableGroupRead, TableGroupUpdate
from schemas.table_schemas import TableCreate, TableRead, TableUpdate
from fastapi.encoders import jsonable_encoder
from core.security import require_any, require_admin
from services import floor_service, table_service

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
    return StreamingResponse(event_generator(request, floor_id), media_type="text/event-stream")


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
async def create_table(payload: TableCreate, session: Session = Depends(get_session), current_user: User = Depends(require_admin)):
    new_table = table_service.create_new_table(
        session=session, table_data=payload)
    table_read = TableRead.model_validate(new_table, from_attributes=True)
    event_data = json.dumps(
        {"action": "create_table", "table": jsonable_encoder(table_read)})
    floor_id = new_table.current_group.floor_id

    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Mesa creada exitosamente", "data": table_read}


@router.patch("/tables/{table_id}")
async def update_table(payload: TableUpdate, table_id: int, session: Session = Depends(get_session), current_user: User = Depends(require_admin)):
    new_table = table_service.update_table(
        session=session, table_id=table_id, table_data=payload)
    table_read = TableRead.model_validate(new_table, from_attributes=True)
    event_data = json.dumps(
        {"action": "update_table", "table": jsonable_encoder(table_read)})
    floor_id = new_table.current_group.floor_id
    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Mesa actualizada exitosamente", "data": table_read}


@router.post("/tablegroups")
async def create_group(payload: TableGroupCreate, session: Session = Depends(get_session), current_user: User = Depends(require_admin)):
    new_table = table_service.group_tables(
        session=session, table_data=payload)
    table_read = TableGroupRead.model_validate(new_table, from_attributes=True)
    event_data = json.dumps(
        {"action": "create_group", "tablegroup": jsonable_encoder(table_read)})
    floor_id = new_table.floor_id

    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Grupo creado exitosamente", "data": table_read}


@router.patch("/tablegroups/{tablegroup_id}")
async def update_group(payload: TableGroupUpdate, tablegroup_id: int, session: Session = Depends(get_session), current_user: User = Depends(require_admin)):
    new_table = table_service.update_tablegroup(
        session=session, group_id=tablegroup_id, group_data=payload)
    table_read = TableGroupRead.model_validate(new_table, from_attributes=True)
    event_data = json.dumps(
        {"action": "update_group", "tablegroup": jsonable_encoder(table_read)})
    floor_id = new_table.floor_id
    if floor_id in connected_clients:
        for queue in connected_clients[floor_id]:
            await queue.put(event_data)

    return {"message": "Grupo actualizado exitosamente", "data": table_read}

