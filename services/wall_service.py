from sqlmodel import Session
from models.wall import Wall
from schemas.wall_schemas import WallCreate, WallUpdate


def create_new_wall(session: Session, wall_data: WallCreate) -> Wall:
    db_wall = Wall(
        floor_id=wall_data.floor_id,
        x1=wall_data.x1,
        y1=wall_data.y1,
        x2=wall_data.x2,
        y2=wall_data.y2,
        isDoor=wall_data.isDoor
    )
    session.add(db_wall)
    session.commit()
    session.refresh(db_wall)
    return db_wall


def update_wall(session: Session, wall_id: int, wall_data: WallUpdate) -> Wall | None:
    db_wall = session.get(Wall, wall_id)
    if not db_wall:
        return None
    
    update_data = wall_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_wall, key, value)
        
    session.commit()
    session.refresh(db_wall)
    return db_wall


def delete_wall(session: Session, wall_id: int) -> bool:
    db_wall = session.get(Wall, wall_id)
    if not db_wall:
        return False
    session.delete(db_wall)
    session.commit()
    return True
