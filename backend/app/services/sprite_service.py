import os
import uuid
import base64
import openai
import logging
from typing import List
from ..models.sprite import Sprite
from ..utils.database import get_db
from .prompt_service import PromptService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI with API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")

# Backend URL for external access
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class SpriteService:
    def __init__(self):
        self.prompt_service = PromptService()

    async def generate_sprite(self, description: str) -> Sprite:
        try:
            logger.info("\n" + "="*80)
            logger.info("SPRITE GENERATION STARTED")
            logger.info(f"User description: {description}")
            logger.info("="*80 + "\n")
            
            # Format the user's prompt
            formatted_prompt = await self.prompt_service.format_sprite_prompt(description)
            
            logger.info("\n" + "="*80)
            logger.info("GENERATING IMAGE WITH GPT-IMAGE-1")
            logger.info(f"Using prompt: {formatted_prompt}")
            logger.info("="*80 + "\n")
            
            # Generate the base sprite image using gpt-image-1 with correct parameters
            response = openai.images.generate(
                model="gpt-image-1",
                prompt=formatted_prompt,
                size="1024x1024",
                background="transparent",  # Set transparent background
                quality="high",  # Use high quality for gpt-image-1
                output_format="png"  # PNG supports transparency
            )
            
            # Get base64 image data (gpt-image-1 always returns base64)
            image_base64 = response.data[0].b64_json
            
            # Save the image to a file in the static directory
            image_filename = f"{uuid.uuid4()}.png"
            static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
            
            # Create static directory if it doesn't exist
            os.makedirs(static_dir, exist_ok=True)
            
            image_path = os.path.join(static_dir, image_filename)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            
            # Create full URL for the image with domain
            image_url = f"{BACKEND_URL}/static/{image_filename}"
            
            logger.info("Base image generated successfully")
            logger.info(f"Image saved to: {image_path}")
            logger.info(f"Image URL: {image_url}")
            
            # Create sprite record with base image
            sprite = Sprite(
                id=str(uuid.uuid4()),
                url=image_url,
                description=description,
                is_base_image=True  # Mark this as a base image
            )
            
            # Save to database
            logger.info("Saving sprite to database...")
            db = next(get_db())
            db.add(sprite)
            db.commit()
            db.refresh(sprite)
            logger.info(f"Sprite saved with ID: {sprite.id}")
            logger.info("\n" + "="*80)
            logger.info("SPRITE GENERATION COMPLETE")
            logger.info("="*80 + "\n")
            
            return sprite
        except Exception as e:
            logger.error("\n" + "="*80)
            logger.error("SPRITE GENERATION FAILED")
            logger.error(f"Error in generate_sprite: {str(e)}", exc_info=True)
            logger.error("="*80 + "\n")
            raise Exception(f"Failed to generate sprite: {str(e)}")

    async def get_sprite(self, sprite_id: str) -> Sprite:
        try:
            db = next(get_db())
            return db.query(Sprite).filter(Sprite.id == sprite_id).first()
        except Exception as e:
            logger.error(f"Error in get_sprite: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get sprite: {str(e)}")
    
    async def get_all_sprites(self) -> List[Sprite]:
        try:
            logger.info("Fetching all sprites from database")
            db = next(get_db())
            sprites = db.query(Sprite).filter(Sprite.is_base_image == True).order_by(Sprite.created_at.desc()).all()
            logger.info(f"Found {len(sprites)} sprites")
            # Ensure URLs are fully qualified
            for sprite in sprites:
                if sprite.url.startswith("/"):
                    sprite.url = f"{BACKEND_URL}{sprite.url}"
            return sprites
        except Exception as e:
            logger.error(f"Error in get_all_sprites: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get all sprites: {str(e)}") 