from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.security import require_admin, require_any
from database import get_session
from models.user import User
from schemas.category_schemas import CategoryCreate, CategoryRead
from services import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=CategoryRead)
def create_category_endpoint(
    payload: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    new_category = category_service.create_new_category(
        session=session, category_data=payload
    )
    return new_category


@router.put("/", response_model=CategoryRead)
def update_category_endpoint(
    category_id: int,
    payload: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    category = category_service.update_category(
        session=session, category_id=category_id, category_data=payload
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("", response_model=list[CategoryRead])
def read_categories_endpoint(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_any),
):
    categories = category_service.get_all_categories(session=session)
    return categories
