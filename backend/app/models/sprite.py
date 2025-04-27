from sqlalchemy import Column, String, Text, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..utils.database import Base

class Sprite(Base):
    __tablename__ = "sprites"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    is_base_image = Column(Boolean, default=True)  # Indicates if this is a base image for animations
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Add edit history tracking
    parent_id = Column(String, ForeignKey("sprites.id"), nullable=True)
    edit_description = Column(Text, nullable=True)  # Description of the edit made
    
    # Relationships
    animations = relationship("Animation", back_populates="base_sprite", cascade="all, delete-orphan")
    
    # Self-referential relationship for edit history
    parent = relationship("Sprite", remote_side=[id], backref="children", uselist=False) 