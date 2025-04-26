import os
import uuid
from typing import List
import openai
from ..models.animation import Animation
from ..utils.database import get_db

# Initialize OpenAI with API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class AnimationService:
    async def generate_animation(self, base_sprite_id: str, animation_type: str) -> Animation:
        try:
            # Get base sprite description
            db = next(get_db())
            base_sprite = db.query(Sprite).filter(Sprite.id == base_sprite_id).first()
            if not base_sprite:
                raise Exception("Base sprite not found")

            response = openai.Image.create(
                prompt=f"Create a {animation_type} animation frame for this character: {base_sprite.description}. The sprite should maintain the same style and proportions as the base sprite.",
                n=1,
                size="1024x1024"
            )
            
            animation = Animation(
                id=str(uuid.uuid4()),
                url=response.data[0].url,
                animation_type=animation_type,
                base_sprite_id=base_sprite_id
            )
            
            # Save to database
            db.add(animation)
            db.commit()
            db.refresh(animation)
            
            return animation
        except Exception as e:
            raise Exception(f"Failed to generate animation: {str(e)}")

    async def get_animation(self, animation_id: str) -> Animation:
        db = next(get_db())
        return db.query(Animation).filter(Animation.id == animation_id).first()

    async def get_sprite_animations(self, sprite_id: str) -> List[Animation]:
        db = next(get_db())
        return db.query(Animation).filter(Animation.base_sprite_id == sprite_id).all() 