import os
import uuid
from openai import OpenAI
from ..models.sprite import Sprite
from ..utils.database import get_db

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SpriteService:
    async def generate_sprite(self, description: str) -> Sprite:
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=f"Create a 2D sprite for a character based on this description: {description}. The sprite should be in a simple, clean style suitable for a 2D game.",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            sprite = Sprite(
                id=str(uuid.uuid4()),
                url=response.data[0].url,
                description=description
            )
            
            # Save to database
            db = next(get_db())
            db.add(sprite)
            db.commit()
            db.refresh(sprite)
            
            return sprite
        except Exception as e:
            raise Exception(f"Failed to generate sprite: {str(e)}")

    async def get_sprite(self, sprite_id: str) -> Sprite:
        db = next(get_db())
        return db.query(Sprite).filter(Sprite.id == sprite_id).first() 