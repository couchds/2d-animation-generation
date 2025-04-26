from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...services.sprite_service import SpriteService
from ...models.sprite import Sprite as SpriteModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
sprite_service = SpriteService()

class SpriteRequest(BaseModel):
    description: str

class SpriteEditRequest(BaseModel):
    spriteId: str
    prompt: str

class SpriteResponse(BaseModel):
    id: str
    url: str
    description: str
    parent_id: Optional[str] = None
    edit_description: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True  # Allows converting ORM model instances to response models
        
        # Define a JSON schema extra to handle JSON serialization of datetime objects
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        }

@router.post("/generate", response_model=SpriteResponse)
async def generate_sprite(request: SpriteRequest):
    try:
        logger.info(f"Received request to generate sprite with description: {request.description}")
        sprite = await sprite_service.generate_sprite(request.description)
        logger.info(f"Successfully generated sprite with ID: {sprite.id}")
        return sprite
    except Exception as e:
        logger.error(f"Error generating sprite: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit", response_model=SpriteResponse)
async def edit_sprite(request: SpriteEditRequest):
    try:
        logger.info(f"Received request to edit sprite {request.spriteId} with prompt: {request.prompt}")
        sprite = await sprite_service.edit_sprite_image(request.spriteId, request.prompt)
        logger.info(f"Successfully edited sprite with ID: {sprite.id}")
        return sprite
    except Exception as e:
        logger.error(f"Error editing sprite: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{sprite_id}", response_model=Dict[str, Any])
async def get_sprite_history(sprite_id: str):
    try:
        logger.info(f"Received request to get edit history for sprite: {sprite_id}")
        history = await sprite_service.get_sprite_history(sprite_id)
        logger.info(f"Successfully retrieved history for sprite: {sprite_id}")
        return history
    except Exception as e:
        logger.error(f"Error getting sprite history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sprite_id}", response_model=SpriteResponse)
async def get_sprite(sprite_id: str):
    try:
        sprite = await sprite_service.get_sprite(sprite_id)
        if not sprite:
            raise HTTPException(status_code=404, detail="Sprite not found")
        return sprite
    except Exception as e:
        logger.error(f"Error getting sprite: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[SpriteResponse])
async def get_all_sprites():
    try:
        logger.info("Received request to get all sprites")
        sprites = await sprite_service.get_all_sprites()
        logger.info(f"Successfully retrieved {len(sprites)} sprites")
        return sprites
    except Exception as e:
        logger.error(f"Error getting all sprites: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 