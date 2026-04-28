from sqlmodel import Session, select
from core import security
from models.user import User
from sqlalchemy.orm import selectinload

from schemas.user_schemas import UserCreate, UserUpdate


def create_new_user(session: Session, user_data: UserCreate) -> User:
    db_user = User(
        username=user_data.username,
        fname=user_data.fname,
        lname=user_data.lname,
        phone=user_data.phone,
        hashed_password=security.get_password_hash(user_data.password),
        role=user_data.role)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(session: Session, user_id: int, user_data: UserUpdate) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        return None
    db_user.hashed_password = security.get_password_hash(
        user_data.password) if user_data.password else db_user.hashed_password
    db_user.fname = user_data.fname or db_user.fname
    db_user.lname = user_data.lname or db_user.lname
    db_user.role = user_data.role or db_user.role
    db_user.phone = user_data.phone or db_user.phone
    session.commit()
    session.refresh(db_user)
    return db_user


def deactivate_user(session: Session, user_id: int) -> bool:
    db_user = session.get(User, user_id)
    if not db_user:
        return False
    db_user.is_active = False
    session.commit()
    session.refresh(db_user)
    return True


def get_all_users(session: Session) -> list[User]:
    statement = select(User)
    return session.exec(statement).all()
