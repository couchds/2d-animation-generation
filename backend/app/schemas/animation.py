from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FrameBase(BaseModel):
    url: str
    prompt: Optional[str] = None
    order: int

class FrameCreate(FrameBase):
    pass

class FrameUpdate(BaseModel):
    url: Optional[str] = None
    prompt: Optional[str] = None
    order: Optional[int] = None

class Frame(FrameBase):
    id: str
    animation_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class AnimationBase(BaseModel):
    name: str
    base_sprite_id: str
    animation_type: Optional[str] = None
    fps: int = Field(default=12, ge=1, le=60)

class AnimationCreate(AnimationBase):
    pass

class AnimationUpdate(BaseModel):
    name: Optional[str] = None
    animation_type: Optional[str] = None
    fps: Optional[int] = Field(default=None, ge=1, le=60)

class Animation(AnimationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    frames: List[Frame] = []
    
    class Config:
        orm_mode = True

class FrameGenerateRequest(BaseModel):
    animation_id: str
    prompt: str
    num_frames: int = Field(default=1, ge=1, le=24)
    starting_order: Optional[int] = None  # If None, will append to end

class FrameReorderRequest(BaseModel):
    animation_id: str
    frame_orders: List[dict] = Field(..., description="List of {frame_id: str, order: int} pairs")

class SpriteSheetRequest(BaseModel):
    animation_id: str
    column_count: Optional[int] = None  # If None, will use a square layout 