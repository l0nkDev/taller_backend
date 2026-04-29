from sqlmodel import Session
from schemas.dish_schemas import DishCreate, DishUpdate
from services.dish_service import create_new_dish, update_dish


def test_create_new_dish_creates_initial_price(session: Session):
    # Arrange
    dish_in = DishCreate(
        name="Silpancho",
        price=35.0,
        category_id=1,
        available=True,
        description="Traditional dish",
    )

    # Act
    db_dish = create_new_dish(session, dish_in)

    # Assert
    assert db_dish.id is not None
    assert len(db_dish.prices) == 1
    assert db_dish.prices[0].price == 35.0
    assert db_dish.prices[0].is_active is True


def test_update_dish_price_change(session: Session):
    # Arrange
    initial_data = DishCreate(
        name="Majadito",
        description="",
        available=True,
        price=25.0,
        category_id=1,
    )
    db_dish = create_new_dish(session, initial_data)
    original_price_id = db_dish.prices[0].id

    # Act
    update_data = DishUpdate(price=30.0)
    updated_dish = update_dish(session, db_dish.id, update_data)

    # Assert
    assert len(updated_dish.prices) == 2
    active_price = next(p for p in updated_dish.prices if p.is_active)
    old_price = next(
        p for p in updated_dish.prices if p.id == original_price_id
    )
    assert active_price.price == 30.0
    assert old_price.is_active is False
    assert old_price.price == 25.0


def test_update_dish_same_price_does_not_create_new_record(session: Session):
    # Arrange
    initial_data = DishCreate(
        name="Locro", description="", available=True, price=20.0, category_id=1
    )
    db_dish = create_new_dish(session, initial_data)

    # Act
    update_data = DishUpdate(price=20.0)
    updated_dish = update_dish(session, db_dish.id, update_data)

    # Assert
    assert len(updated_dish.prices) == 1
    assert updated_dish.prices[0].is_active is True
