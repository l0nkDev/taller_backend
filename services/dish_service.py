from sqlmodel import Session, select
from models.dish import Dish
from models.dish_price import DishPrice
from schemas.dish_schemas import DishCreate, DishUpdate


def create_new_dish(session: Session, dish_data: DishCreate) -> Dish:
    db_dish = Dish(
        name=dish_data.name,
        category_id=dish_data.category_id,
        available=dish_data.available,
        description=dish_data.description,
    )
    session.add(db_dish)
    session.flush()
    price = DishPrice(dish_id=db_dish.id, price=dish_data.price)
    session.add(price)
    session.commit()
    session.refresh(db_dish)
    return db_dish


def update_dish(
    session: Session, dish_id: int, dish_data: DishUpdate
) -> Dish | None:
    db_dish = session.get(Dish, dish_id)
    if not db_dish:
        return None
    if dish_data.price is not None:
        current_price = next((p for p in db_dish.prices if p.is_active), None)
        if current_price.price != dish_data.price:
            current_price.is_active = False
            new_price = DishPrice(dish_id=db_dish.id, price=dish_data.price)
            session.add(current_price)
            session.add(new_price)
    db_dish.name = dish_data.name or db_dish.name
    db_dish.category_id = dish_data.category_id or db_dish.category_id
    db_dish.available = (
        dish_data.available
        if dish_data.available is not None
        else db_dish.available
    )
    db_dish.description = dish_data.description or db_dish.description
    session.commit()
    session.refresh(db_dish)
    return db_dish


def get_all_dishes(session: Session) -> list[Dish]:
    statement = select(Dish).order_by(Dish.id.asc())
    return session.exec(statement).all()
