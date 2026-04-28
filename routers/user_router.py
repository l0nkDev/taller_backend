from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.security import require_admin
from database import get_session
from models.user import User
from schemas.user_schemas import UserCreate, UserRead, UserUpdate
from services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserRead)
def create_user_endpoint(
        payload: UserCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(require_admin)
    ):
    new_user = user_service.create_new_user(session=session, user_data=payload)
    return new_user


@router.put("", response_model=UserRead)
def update_USER_endpoint(
        user_id: int,
        payload: UserUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(require_admin)
    ):
    user = user_service.update_user(
        session=session, user_id=user_id, user_data=payload)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=list[UserRead])
def read_dishes_endpoint(
        session: Session = Depends(get_session),
        current_user: User = Depends(require_admin)
        ):
    users = user_service.get_all_users(session=session)
    return users


@router.delete("")
def read_dishes_endpoint(
        user_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(require_admin)
    ):
    user = user_service.deactivate_user(session=session, user_id=user_id)
    return user
