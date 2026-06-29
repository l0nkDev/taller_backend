import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from core.security import require_admin, require_any
from database import get_session
from models.user import User
from schemas.order_detail_schemas import OrderDetailCreate, OrderDetailUpdate
from schemas.order_schemas import OrderBulkSync, OrderRead
from schemas.payment_schemas import PaymentCreate, PaymentRead
from services import order_detail_service, order_service

router = APIRouter(prefix="/orders", tags=["Orders"])

connected_order_clients = []


# --- 1. CONFIGURACIÓN SSE ---
async def order_event_generator(request: Request):
    client_queue = asyncio.Queue()
    connected_order_clients.append(client_queue)
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
        connected_order_clients.remove(client_queue)


@router.get("/stream")
async def sse_orders_updates(request: Request):
    return StreamingResponse(
        order_event_generator(request), media_type="text/event-stream"
    )


async def notify_order_clients(action: str, payload: dict = None):
    event_data = json.dumps({"action": action, "data": payload})
    for queue in connected_order_clients:
        await queue.put(event_data)


@router.post("", response_model=OrderRead)
def create_order_detail_endpoint(
    payload: OrderDetailCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    new_order_detail = order_detail_service.create_new_order_detail(
        session=session, order_detail_data=payload
    )
    return new_order_detail


@router.put("", response_model=OrderRead)
async def update_order_detail_endpoint(
    order_detail_id: int,
    payload: OrderDetailUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_any),
):
    order = order_detail_service.update_order_detail(
        session=session,
        order_detail_id=order_detail_id,
        order_detail_data=payload,
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order_read = OrderRead.model_validate(order, from_attributes=True)
    await notify_order_clients("update_order", jsonable_encoder(order_read))

    return order


@router.delete("", response_model=bool)
def delete_order_detail_endpoint(
    order_detail_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    result = order_detail_service.delete_order_detail(
        session=session, order_detail_id=order_detail_id
    )
    if result:
        return result
    raise HTTPException(status_code=404, detail="Order not found")


@router.get("/at", response_model=OrderRead)
def get_order_at_endpoint(
    tablegroup_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_any),
):
    result = order_service.get_order_by_tablegroup(
        session=session, tablegroup_id=tablegroup_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.get("/active", response_model=list[OrderRead])
def get_active_orders_endpoint(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_any),
):
    return order_service.get_all_active_orders(session)


@router.post("/bulk-sync", response_model=OrderRead)
async def sync_bulk_order_endpoint(
    payload: OrderBulkSync,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_any),
):
    order = order_service.sync_bulk_order(session=session, order_data=payload)
    order_read = OrderRead.model_validate(order, from_attributes=True)

    await notify_order_clients("update_order", jsonable_encoder(order_read))
    return order


@router.post("/pay", response_model=PaymentRead)
async def pay_order_endpoint(
    order_id: int,
    payload: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    result = order_service.pay_order(
        session=session, order_id=order_id, payment_data=payload
    )
    if result:
        await notify_order_clients("remove_order", {"order_id": order_id})
        return result

    raise HTTPException(status_code=404, detail="Order not found")


@router.delete("/cancel", response_model=bool)
async def cancel_order_endpoint(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    result = order_service.delete_order(session=session, order_id=order_id)
    if result:
        await notify_order_clients("remove_order", {"order_id": order_id})
        return result
    raise HTTPException(status_code=404, detail="Order not found")
