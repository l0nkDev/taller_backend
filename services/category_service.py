from fastapi import Depends
from sqlmodel import Session, select

from core.security import require_admin
from models.category import Category
from models.user import User
from schemas.category_schemas import CategoryCreate


def create_new_category(
    session: Session,
    category_data: CategoryCreate,
    current_user: User = Depends(require_admin),
) -> Category:
    db_category = Category(name=category_data.name)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def update_category(
    session: Session,
    category_id: int,
    category_data: CategoryCreate,
    current_user: User = Depends(require_admin),
) -> Category | None:
    db_category = session.get(Category, category_id)
    if not db_category:
        return None
    db_category.name = category_data.name
    session.commit()
    session.refresh(db_category)
    return db_category


def get_all_categories(session: Session) -> list[Category]:
    statement = select(Category).order_by(Category.id.asc())
    return session.exec(statement).all()
