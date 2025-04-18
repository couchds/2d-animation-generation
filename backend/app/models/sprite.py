from sqlalchemy import Column, String, Text
from ..utils.database import Base

class Sprite(Base):
    __tablename__ = "sprites"

    id = Column(String, primary_key=True, index=True)
    url = Column(String)
    description = Column(Text) 