from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from ..utils.database import Base

class Animation(Base):
    __tablename__ = "animations"

    id = Column(String, primary_key=True, index=True)
    url = Column(String)
    animation_type = Column(String)
    base_sprite_id = Column(String, ForeignKey("sprites.id"))
    
    base_sprite = relationship("Sprite", back_populates="animations") 