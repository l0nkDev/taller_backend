from sqlmodel import Session, select

from models.dish_price import DishPrice
from models.order import Order
from models.order_detail import OrderDetail
from schemas.order_detail_schemas import OrderDetailCreate, OrderDetailUpdate

def create_new_order_detail(session: Session, order_detail_data: OrderDetailCreate) -> Order:
    price = session.exec(select(DishPrice).where(DishPrice.dish_id == order_detail_data.dish_id, DishPrice.is_active == True)).first()
    db_order_detail = OrderDetail(
        price_id=price.id,
        quantity=order_detail_data.quantity,
        discount=order_detail_data.discount,
        status=order_detail_data.status
    )
    db_order = session.exec(select(Order).where(Order.tablegroup_id == order_detail_data.tablegroup_id,
        Order.was_paid == False, Order.was_cancelled == False)).first()
    if db_order is None:
        db_order = Order(tablegroup_id=order_detail_data.tablegroup_id)
        session.add(db_order)
        session.flush()
        session.refresh(db_order)
    db_order_detail.order_id = db_order.id
    session.add(db_order_detail)
    session.commit()
    session.refresh(db_order)
    return db_order

def update_order_detail(session: Session, order_detail_id: int, order_detail_data: OrderDetailUpdate) -> Order | None:
    db_order_detail = session.get(OrderDetail, order_detail_id)
    if not db_order_detail:
        return None
    if order_detail_data.dish_id is not None:
        db_order_detail.dish_id = order_detail_data.dish_id
    if order_detail_data.quantity is not None:
        db_order_detail.quantity = order_detail_data.quantity
    session.commit()
    session.refresh(db_order_detail)
    return db_order_detail.order

def delete_order_detail(session: Session, order_detail_id: int) -> bool:
    db_order_detail = session.get(OrderDetail, order_detail_id)
    if not db_order_detail:
        return False
    session.delete(db_order_detail)
    session.commit()
    return True