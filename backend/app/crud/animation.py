from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.animation import Animation, Frame
from app.schemas.animation import AnimationCreate, AnimationUpdate, FrameCreate, FrameUpdate


def get_animation(db: Session, animation_id: str) -> Optional[Animation]:
    return db.query(Animation).filter(Animation.id == animation_id).first()


def get_animations(db: Session, skip: int = 0, limit: int = 100) -> List[Animation]:
    return db.query(Animation).order_by(Animation.created_at.desc()).offset(skip).limit(limit).all()


def get_animations_by_base_sprite(db: Session, base_sprite_id: str) -> List[Animation]:
    return db.query(Animation).filter(Animation.base_sprite_id == base_sprite_id).all()


def create_animation(db: Session, animation: AnimationCreate) -> Animation:
    db_animation = Animation(
        id=str(uuid.uuid4()),
        name=animation.name,
        base_sprite_id=animation.base_sprite_id,
        animation_type=animation.animation_type,
        fps=animation.fps,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_animation)
    db.commit()
    db.refresh(db_animation)
    return db_animation


def update_animation(db: Session, animation_id: str, animation: AnimationUpdate) -> Optional[Animation]:
    db_animation = get_animation(db, animation_id)
    if not db_animation:
        return None
    
    update_data = animation.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_animation, key, value)
    
    db.commit()
    db.refresh(db_animation)
    return db_animation


def delete_animation(db: Session, animation_id: str) -> bool:
    db_animation = get_animation(db, animation_id)
    if not db_animation:
        return False
    
    # Delete all frames associated with this animation
    db.query(Frame).filter(Frame.animation_id == animation_id).delete()
    
    db.delete(db_animation)
    db.commit()
    return True


# Frame CRUD operations

def get_frame(db: Session, frame_id: str) -> Optional[Frame]:
    return db.query(Frame).filter(Frame.id == frame_id).first()


def get_frames_by_animation(db: Session, animation_id: str) -> List[Frame]:
    return db.query(Frame).filter(Frame.animation_id == animation_id).order_by(Frame.order).all()


def create_frame(db: Session, frame: FrameCreate, animation_id: str) -> Frame:
    db_frame = Frame(
        id=str(uuid.uuid4()),
        animation_id=animation_id,
        url=frame.url,
        prompt=frame.prompt,
        order=frame.order,
        created_at=datetime.utcnow()
    )
    db.add(db_frame)
    db.commit()
    db.refresh(db_frame)
    return db_frame


def create_frames_batch(db: Session, frames: List[FrameCreate], animation_id: str) -> List[Frame]:
    db_frames = []
    for frame in frames:
        db_frame = Frame(
            id=str(uuid.uuid4()),
            animation_id=animation_id,
            url=frame.url,
            prompt=frame.prompt,
            order=frame.order,
            created_at=datetime.utcnow()
        )
        db.add(db_frame)
        db_frames.append(db_frame)
    
    db.commit()
    for frame in db_frames:
        db.refresh(frame)
    
    return db_frames


def update_frame(db: Session, frame_id: str, frame: FrameUpdate) -> Optional[Frame]:
    db_frame = get_frame(db, frame_id)
    if not db_frame:
        return None
    
    update_data = frame.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_frame, key, value)
    
    db.commit()
    db.refresh(db_frame)
    return db_frame


def update_frame_orders(db: Session, animation_id: str, frame_orders: List[dict]) -> bool:
    for item in frame_orders:
        frame_id = item.get("frame_id")
        new_order = item.get("order")
        
        if frame_id and new_order is not None:
            frame = get_frame(db, frame_id)
            if frame and frame.animation_id == animation_id:
                frame.order = new_order
    
    db.commit()
    return True


def delete_frame(db: Session, frame_id: str) -> bool:
    db_frame = get_frame(db, frame_id)
    if not db_frame:
        return False
    
    db.delete(db_frame)
    db.commit()
    return True


def delete_frames_by_animation(db: Session, animation_id: str) -> int:
    result = db.query(Frame).filter(Frame.animation_id == animation_id).delete()
    db.commit()
    return result 