from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...services.sprite_service import SpriteService

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
        sprite = await sprite_service.generate_sprite(request.description)
        return sprite
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sprite_id}", response_model=SpriteResponse)
async def get_sprite(sprite_id: str):
    try:
        sprite = await sprite_service.get_sprite(sprite_id)
        if not sprite:
            raise HTTPException(status_code=404, detail="Sprite not found")
        return sprite
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 