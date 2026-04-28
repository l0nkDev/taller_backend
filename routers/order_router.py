from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.security import require_admin, require_any
from database import get_session
from models.user import User
from schemas.order_detail_schemas import OrderDetailCreate, OrderDetailUpdate
from schemas.order_schemas import OrderRead
from schemas.payment_schemas import PaymentCreate, PaymentRead
from services import order_detail_service, order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderRead)
def create_order_detail_endpoint(payload: OrderDetailCreate, session: Session = Depends(get_session),
                                 current_user: User = Depends(require_admin)):
    new_order_detail = order_detail_service.create_new_order_detail(
        session=session, order_detail_data=payload)
    return new_order_detail


@router.put("/", response_model=OrderRead)
def update_order_detail_endpoint(order_detail_id: int, payload: OrderDetailUpdate, session: Session = Depends(get_session),
                                 current_user: User = Depends(require_admin)):
    order = order_detail_service.update_order_detail(
        session=session, order_detail_id=order_detail_id, order_detail_data=payload)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.delete("/", response_model=bool)
def delete_order_detail_endpoint(order_detail_id: int, session: Session = Depends(get_session),
                                 current_user: User = Depends(require_admin)):
    result = order_detail_service.delete_order_detail(
        session=session, order_detail_id=order_detail_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Order not found")


@router.delete("/cancel/", response_model=bool)
def delete_order_detail_endpoint(order_id: int, session: Session = Depends(get_session),
                                 current_user: User = Depends(require_admin)):
    result = order_service.delete_order(session=session, order_id=order_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Order not found")


@router.get("/at/", response_model=OrderRead)
def delete_order_detail_endpoint(tablegroup_id: int, session: Session = Depends(get_session),
                                 current_user: User = Depends(require_any)):
    result = order_service.get_order_by_tablegroup(
        session=session, tablegroup_id=tablegroup_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.post("/pay/", response_model=PaymentRead)
def delete_order_detail_endpoint(order_id: int, payload: PaymentCreate, session: Session = Depends(get_session),
                                 current_user: User = Depends(require_admin)):
    result = order_service.pay_order(
        session=session, order_id=order_id, payment_data=payload)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Order not found")
