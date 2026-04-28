from fastapi import APIRouter, Depends
from sqlmodel import Session

from core.security import require_admin
from database import get_session
from models.user import User
from schemas.table_schemas import TableCreate, TableRead
from services import table_service

router = APIRouter(prefix="/tables", tags=["Tables"])

@router.post("", response_model=TableRead)
def create_floor_endpoint(payload: TableCreate, session: Session = Depends(get_session),
        current_user: User = Depends(require_admin)):
    new_table = table_service.create_new_table(session=session, table_data=payload)
    return new_table