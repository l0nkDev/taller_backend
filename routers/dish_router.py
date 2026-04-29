from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.security import require_admin, require_any
from database import get_session
from models.user import User
from schemas.dish_schemas import DishCreate, DishRead, DishUpdate
from services import dish_service

router = APIRouter(prefix="/dishes", tags=["Dishes"])


@router.post("", response_model=DishRead)
def create_dish_endpoint(
    payload: DishCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    new_dish = dish_service.create_new_dish(session=session, dish_data=payload)
    return new_dish


@router.put("/", response_model=DishRead)
def update_dish_endpoint(
    dish_id: int,
    payload: DishUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    dish = dish_service.update_dish(
        session=session, dish_id=dish_id, dish_data=payload
    )
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@router.get("", response_model=list[DishRead])
def read_dishes_endpoint(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_any),
):
    dishes = dish_service.get_all_dishes(session=session)
    return dishes
