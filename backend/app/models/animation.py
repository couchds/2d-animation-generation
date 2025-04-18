from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..utils.database import Base

class Animation(Base):
    __tablename__ = "animations"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    animation_type = Column(String, nullable=False)
    base_sprite_id = Column(String, ForeignKey("sprites.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    base_sprite = relationship("Sprite", back_populates="animations") 