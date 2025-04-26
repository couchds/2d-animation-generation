from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from typing import List
from ...services.sprite_service import SpriteService
from ...models.sprite import Sprite as SpriteModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
sprite_service = SpriteService()

class SpriteRequest(BaseModel):
    description: str

class SpriteResponse(BaseModel):
    id: str
    url: str
    description: str

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