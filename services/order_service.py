from sqlmodel import Session, select

from models.dish_price import DishPrice
from models.order import Order
from models.order_detail import OrderDetail, OrderDetail
from models.order_detail import DetailStatus
from models.payment import Payment
from schemas.order_schemas import OrderBulkSync
from schemas.payment_schemas import PaymentCreate


def get_all_orders(session: Session) -> list[Order]:
    return session.exec(select(Order)).all()


def get_order_by_tablegroup(
    session: Session, tablegroup_id: int
) -> Order | None:
    return session.exec(
        select(Order).where(
            Order.tablegroup_id == tablegroup_id,
            Order.was_cancelled == False,
            Order.was_paid == False,
        )
    ).first()


def delete_order(session: Session, order_id: int) -> bool:
    db_order = session.get(Order, order_id)
    if not db_order:
        return False
    db_order.was_paid = False
    db_order.was_cancelled = True
    session.commit()
    return True


def pay_order(
    session: Session, order_id: int, payment_data: PaymentCreate
) -> Payment:
    db_order = session.get(Order, order_id)
    if not db_order:
        return None
    if db_order.was_paid == True:
        return session.exec(
            select(Payment).where(Payment.order_id == order_id)
        ).first()
    db_order.was_paid = True
    total = 0
    for detail in db_order.detail:
        if detail.status != "X":
            total += (detail.price.price - detail.discount) * detail.quantity
    payment = Payment(
        method=payment_data.method, total=total, order_id=db_order.id
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment

def get_all_active_orders(session: Session) -> list[Order]:
    # Devuelve todas las órdenes que están vivas en el salón
    return session.exec(
        select(Order).where(Order.was_paid == False, Order.was_cancelled == False)
    ).all()

def sync_bulk_order(session: Session, order_data: OrderBulkSync) -> Order:
    db_order = get_order_by_tablegroup(session, order_data.tablegroup_id)
    
    # Si la mesa no tenía orden, la creamos
    if not db_order:
        db_order = Order(tablegroup_id=order_data.tablegroup_id)
        session.add(db_order)
        session.flush()
    else:
        # Si ya tenía orden, limpiamos los items "Borrador" (TAKEN) para reemplazarlos
        # (Los items que ya están "IN_KITCHEN" o "COOKING" no se tocan)
        for detail in db_order.detail:
            if detail.status == DetailStatus.TAKEN:
                session.delete(detail)
        session.flush()

    # Insertamos el carrito completo del frontend
    for item in order_data.items:
        price = session.exec(
            select(DishPrice).where(DishPrice.dish_id == item.dish_id, DishPrice.is_active == True)
        ).first()
        
        if price:
            new_detail = OrderDetail(
                price_id=price.id,
                quantity=item.quantity,
                discount=item.discount,
                status=item.status,
                order_id=db_order.id
            )
            session.add(new_detail)
            
    session.commit()
    session.refresh(db_order)
    return db_order
