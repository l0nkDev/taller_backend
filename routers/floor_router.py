from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.security import require_admin, require_any
from database import get_session
from models.user import User
from schemas.floor_schemas import FloorCreate, FloorRead
from services import floor_service

router = APIRouter(prefix="/floors", tags=["Floors"])


@router.post("/", response_model=FloorRead)
def create_floor_endpoint(payload: FloorCreate, session: Session = Depends(get_session),
                          current_user: User = Depends(require_admin)):
    new_floor = floor_service.create_new_floor(
        session=session, floor_data=payload)
    return new_floor


@router.get("/{floor_id}", response_model=FloorRead)
def read_floor_endpoint(floor_id: int, session: Session = Depends(get_session),
                        current_user: User = Depends(require_any)):
    floor = floor_service.get_floor_by_id(session=session, floor_id=floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return floor


@router.get("/", response_model=list[FloorRead])
def read_floors_endpoint(session: Session = Depends(get_session),
                         current_user: User = Depends(require_any)):
    floors = floor_service.get_all_floors(session=session)
    return floors
