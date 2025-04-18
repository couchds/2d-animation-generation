from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from ..utils.database import Base

class Sprite(Base):
    __tablename__ = "sprites"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    animations = relationship("Animation", back_populates="base_sprite", cascade="all, delete-orphan") 