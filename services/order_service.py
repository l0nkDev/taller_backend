from sqlmodel import Session, select

from models.order import Order
from models.payment import Payment
from schemas.payment_schemas import PaymentCreate


def get_all_orders(session: Session) -> list[Order]:
    return session.exec(select(Order)).all()


def get_order_by_tablegroup(
    session: Session, tablegroup_id: int
) -> Order | None:
    return session.exec(
        select(Order).where(
            Order.tablegroup_id == tablegroup_id,
            Order.was_cancelled is False,
            Order.was_paid is False,
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
    if db_order.was_paid is True:
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
