from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship
from ..utils.database import Base
import uuid
from datetime import datetime

class Animation(Base):
    __tablename__ = "animations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False, index=True)
    base_sprite_id = Column(String, ForeignKey("sprites.id"), nullable=False, index=True)
    animation_type = Column(String, nullable=True)  # walk, run, idle, etc.
    fps = Column(Integer, default=12)  # frames per second
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    frames = relationship("Frame", back_populates="animation", cascade="all, delete-orphan", order_by="Frame.order")
    base_sprite = relationship("Sprite", back_populates="animations")
    
    def __repr__(self):
        return f"<Animation(id='{self.id}', name='{self.name}', type='{self.animation_type}')>"

class Frame(Base):
    __tablename__ = "frames"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    animation_id = Column(String, ForeignKey("animations.id"), nullable=False, index=True)
    url = Column(String, nullable=False)  # URL to the image
    prompt = Column(String, nullable=True)  # Original prompt used to generate
    order = Column(Integer, nullable=False)  # Position in the animation sequence
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    animation = relationship("Animation", back_populates="frames")
    
    def __repr__(self):
        return f"<Frame(id='{self.id}', animation_id='{self.animation_id}', order={self.order})>" 