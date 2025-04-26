import os
import uuid
import base64
import openai
import logging
from typing import List, Dict, Any
from sqlalchemy import desc
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

    async def edit_sprite_image(self, sprite_id: str, prompt: str) -> Sprite:
        try:
            logger.info("\n" + "="*80)
            logger.info("SPRITE EDIT STARTED")
            logger.info(f"Sprite ID: {sprite_id}")
            logger.info(f"Edit prompt: {prompt}")
            logger.info("="*80 + "\n")
            
            # Get the original sprite
            db = next(get_db())
            original_sprite = db.query(Sprite).filter(Sprite.id == sprite_id).first()
            
            if not original_sprite:
                raise Exception(f"Sprite with ID {sprite_id} not found")
            
            # Format the edit prompt
            formatted_prompt = await self.prompt_service.format_sprite_prompt(
                f"Edit this sprite: {original_sprite.description}. {prompt}"
            )
            
            logger.info("\n" + "="*80)
            logger.info("EDITING IMAGE WITH GPT-IMAGE-1")
            logger.info(f"Using prompt: {formatted_prompt}")
            logger.info("="*80 + "\n")
            
            # Generate the edited sprite image using gpt-image-1
            response = openai.images.generate(
                model="gpt-image-1",
                prompt=formatted_prompt,
                size="1024x1024",
                background="transparent",
                quality="high",
                output_format="png"
            )
            
            # Get base64 image data
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
            
            logger.info("Edited image generated successfully")
            logger.info(f"Image saved to: {image_path}")
            logger.info(f"Image URL: {image_url}")
            
            # Create sprite record with edited image, including parent relationship
            sprite = Sprite(
                id=str(uuid.uuid4()),
                url=image_url,
                description=original_sprite.description,  # Keep original description
                edit_description=prompt,  # Add the edit description
                parent_id=original_sprite.id,  # Link to parent sprite
                is_base_image=True  # Mark this as a base image
            )
            
            # Save to database
            logger.info("Saving edited sprite to database...")
            db.add(sprite)
            db.commit()
            db.refresh(sprite)
            logger.info(f"Edited sprite saved with ID: {sprite.id}")
            logger.info("\n" + "="*80)
            logger.info("SPRITE EDIT COMPLETE")
            logger.info("="*80 + "\n")
            
            return sprite
        except Exception as e:
            logger.error("\n" + "="*80)
            logger.error("SPRITE EDIT FAILED")
            logger.error(f"Error in edit_sprite_image: {str(e)}", exc_info=True)
            logger.error("="*80 + "\n")
            raise Exception(f"Failed to edit sprite: {str(e)}")

    async def get_sprite(self, sprite_id: str) -> Sprite:
        try:
            db = next(get_db())
            sprite = db.query(Sprite).filter(Sprite.id == sprite_id).first()
            
            if sprite:
                # Convert datetime objects to ISO format strings
                if sprite.created_at:
                    sprite.created_at = sprite.created_at.isoformat()
                if sprite.updated_at:
                    sprite.updated_at = sprite.updated_at.isoformat()
                    
                # Ensure URL is fully qualified
                if sprite.url and sprite.url.startswith("/"):
                    sprite.url = f"{BACKEND_URL}{sprite.url}"
                    
                # Ensure NULL values for parent_id and edit_description are converted to None
                if hasattr(sprite, 'parent_id') and sprite.parent_id is None:
                    sprite.parent_id = None
                if hasattr(sprite, 'edit_description') and sprite.edit_description is None:
                    sprite.edit_description = None
                    
            return sprite
        except Exception as e:
            logger.error(f"Error in get_sprite: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get sprite: {str(e)}")
    
    async def get_all_sprites(self) -> List[Sprite]:
        try:
            logger.info("Fetching all sprites from database")
            db = next(get_db())
            
            # First, get all sprites
            all_sprites = db.query(Sprite).filter(Sprite.is_base_image == True).all()
            logger.info(f"Found {len(all_sprites)} total sprites")
            
            # Create a dictionary to track the latest sprite in each chain
            # Key: root_id, Value: most recent sprite in that chain
            latest_sprites_by_chain = {}
            
            # Process each sprite
            for sprite in all_sprites:
                # First, find the root sprite (the one with no parent)
                root_id = sprite.id
                parent_id = sprite.parent_id
                
                # Traverse up to find the root
                while parent_id:
                    # Look up the parent sprite
                    parent = db.query(Sprite).filter(Sprite.id == parent_id).first()
                    if not parent:
                        break
                    
                    root_id = parent.id
                    parent_id = parent.parent_id
                
                # Now we have the root_id, check if we already have a sprite for this chain
                if root_id in latest_sprites_by_chain:
                    # Compare creation dates
                    existing = latest_sprites_by_chain[root_id]
                    if sprite.created_at > existing.created_at:
                        latest_sprites_by_chain[root_id] = sprite
                else:
                    # First sprite we've seen from this chain
                    latest_sprites_by_chain[root_id] = sprite
            
            # Convert the dictionary to a list
            result_sprites = list(latest_sprites_by_chain.values())
            
            # Sort by created_at (newest first)
            result_sprites.sort(key=lambda x: x.created_at, reverse=True)
            
            logger.info(f"Filtered to {len(result_sprites)} latest sprites (one per timeline)")
            
            # Process each sprite to ensure proper formatting
            for sprite in result_sprites:
                # Convert datetime objects to ISO format strings
                if sprite.created_at:
                    sprite.created_at = sprite.created_at.isoformat()
                if sprite.updated_at:
                    sprite.updated_at = sprite.updated_at.isoformat()
                    
                # Ensure URLs are fully qualified
                if sprite.url and sprite.url.startswith("/"):
                    sprite.url = f"{BACKEND_URL}{sprite.url}"
                    
                # Ensure NULL values for parent_id and edit_description are converted to None
                if hasattr(sprite, 'parent_id') and sprite.parent_id is None:
                    sprite.parent_id = None
                if hasattr(sprite, 'edit_description') and sprite.edit_description is None:
                    sprite.edit_description = None
                    
            return result_sprites
        except Exception as e:
            logger.error(f"Error in get_all_sprites: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get all sprites: {str(e)}")

    async def get_sprite_history(self, sprite_id: str) -> Dict[str, Any]:
        """
        Get the complete edit history of a sprite, including its ancestors and descendants.
        
        Returns a dictionary containing:
        - current: The requested sprite
        - ancestors: List of parent sprites in chronological order (oldest first)
        - children: List of direct child sprites (edits) in chronological order
        - timeline: Combined list of all related sprites in chronological order
        """
        try:
            logger.info(f"Fetching edit history for sprite: {sprite_id}")
            db = next(get_db())
            
            # Get the current sprite
            current_sprite = db.query(Sprite).filter(Sprite.id == sprite_id).first()
            if not current_sprite:
                raise Exception(f"Sprite with ID {sprite_id} not found")
            
            # Ensure URL is fully qualified
            if current_sprite.url.startswith("/"):
                current_sprite.url = f"{BACKEND_URL}{current_sprite.url}"
            
            # Get ancestors (parent chain)
            ancestors = []
            parent_id = current_sprite.parent_id
            
            while parent_id:
                parent = db.query(Sprite).filter(Sprite.id == parent_id).first()
                if not parent:
                    break
                
                # Ensure URL is fully qualified
                if parent.url.startswith("/"):
                    parent.url = f"{BACKEND_URL}{parent.url}"
                
                ancestors.insert(0, parent)  # Insert at the beginning to maintain order
                parent_id = parent.parent_id
            
            # Get children (direct edits of this sprite)
            children = db.query(Sprite).filter(Sprite.parent_id == sprite_id).order_by(Sprite.created_at).all()
            
            # Ensure URLs are fully qualified
            for child in children:
                if child.url.startswith("/"):
                    child.url = f"{BACKEND_URL}{child.url}"
            
            # Create a timeline including ancestors, current, and children
            timeline = ancestors + [current_sprite] + children
            
            # Sort timeline by created_at
            timeline.sort(key=lambda x: x.created_at)
            
            logger.info(f"Found {len(ancestors)} ancestors and {len(children)} children for sprite {sprite_id}")
            
            return {
                "current": current_sprite,
                "ancestors": ancestors,
                "children": children,
                "timeline": timeline
            }
        except Exception as e:
            logger.error(f"Error in get_sprite_history: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get sprite history: {str(e)}") 