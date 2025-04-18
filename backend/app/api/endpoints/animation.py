from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ...services.animation_service import AnimationService

router = APIRouter()
animation_service = AnimationService()

class AnimationRequest(BaseModel):
    base_sprite_id: str
    animation_type: str

class AnimationResponse(BaseModel):
    id: str
    url: str
    animation_type: str
    base_sprite_id: str

@router.post("/generate", response_model=AnimationResponse)
async def generate_animation(request: AnimationRequest):
    try:
        animation = await animation_service.generate_animation(
            request.base_sprite_id,
            request.animation_type
        )
        return animation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{animation_id}", response_model=AnimationResponse)
async def get_animation(animation_id: str):
    try:
        animation = await animation_service.get_animation(animation_id)
        if not animation:
            raise HTTPException(status_code=404, detail="Animation not found")
        return animation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sprite/{sprite_id}", response_model=List[AnimationResponse])
async def get_sprite_animations(sprite_id: str):
    try:
        animations = await animation_service.get_sprite_animations(sprite_id)
        return animations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 