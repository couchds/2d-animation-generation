from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import List, Dict, Any, Optional
from ...services.animation_service import AnimationService
from ...models.animation import Animation
from pydantic import BaseModel

# Create Pydantic model for animation generation request
class AnimationGenerateRequest(BaseModel):
    base_sprite_id: str
    animation_type: str
    num_frames: int = 4  # Default to 4 frames

router = APIRouter()
animation_service = AnimationService()

@router.post("/create", response_model=Dict[str, Any])
async def create_animation(
    name: str = Body(..., description="Name of the animation"),
    base_sprite_id: str = Body(..., description="ID of the base sprite"),
    animation_type: Optional[str] = Body(None, description="Type of animation (walk, run, idle, etc.)"),
    fps: int = Body(12, description="Frames per second for playback")
):
    """Create a new animation for a sprite"""
    try:
        animation = await animation_service.create_animation(
            name=name,
            base_sprite_id=base_sprite_id,
            animation_type=animation_type,
            fps=fps
        )
        return {"id": animation.id, "message": "Animation created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate", response_model=Dict[str, Any])
async def generate_animation(request: AnimationGenerateRequest):
    """Generate a complete animation for a sprite"""
    try:
        # First create an animation
        animation = await animation_service.create_animation(
            name=f"{request.animation_type.capitalize()} Animation",
            base_sprite_id=request.base_sprite_id,
            animation_type=request.animation_type,
            fps=12  # Default value
        )
        
        # Then generate the preset frames
        frames = await animation_service.generate_animation_preset(
            animation_id=animation.id,
            preset_type=request.animation_type,
            num_frames=request.num_frames
        )
        
        # Get the completed animation
        result = await animation_service.get_animation(animation.id)
        
        # Get the URL of the first frame for preview
        if frames and len(frames) > 0:
            url = frames[0].url
        else:
            url = None
        
        return {
            "id": animation.id, 
            "url": url,
            "frames_count": len(frames),
            "message": f"Generated {request.animation_type} animation with {len(frames)} frames"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/frames/generate", response_model=Dict[str, Any])
async def generate_frame(
    animation_id: str = Body(..., description="ID of the animation"),
    prompt: str = Body(..., description="Description for generating this frame"),
    order: Optional[int] = Body(None, description="Position in sequence (if None, appends to end)")
):
    """Generate a new frame for an animation"""
    try:
        frame = await animation_service.generate_frame(
            animation_id=animation_id,
            prompt=prompt,
            order=order
        )
        return {
            "id": frame.id,
            "url": frame.url,
            "order": frame.order,
            "message": "Frame generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/presets/generate", response_model=Dict[str, Any])
async def generate_preset_animation(
    animation_id: str = Body(..., description="ID of the animation"),
    preset_type: str = Body(..., description="Type of animation (walk, run, idle, jump, etc.)"),
    num_frames: int = Body(4, description="Number of frames to generate (default 4, max 24)")
):
    """Generate a preset animation with multiple frames"""
    try:
        # Validate frame count
        if num_frames < 1 or num_frames > 24:
            raise HTTPException(status_code=400, detail="Number of frames must be between 1 and 24")
            
        frames = await animation_service.generate_animation_preset(
            animation_id=animation_id,
            preset_type=preset_type,
            num_frames=num_frames
        )
        return {
            "frames_count": len(frames),
            "animation_id": animation_id,
            "message": f"Generated {len(frames)} frames for {preset_type} animation"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{animation_id}", response_model=Dict[str, Any])
async def get_animation(animation_id: str):
    """Get an animation by ID with all its frames"""
    try:
        animation = await animation_service.get_animation(animation_id)
        if not animation:
            raise HTTPException(status_code=404, detail="Animation not found")
        return animation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sprite/{sprite_id}", response_model=List[Dict[str, Any]])
async def get_sprite_animations(sprite_id: str):
    """Get all animations for a sprite"""
    try:
        animations = await animation_service.get_sprite_animations(sprite_id)
        return animations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{animation_id}", response_model=Dict[str, Any])
async def update_animation(
    animation_id: str,
    name: Optional[str] = Body(None),
    animation_type: Optional[str] = Body(None),
    fps: Optional[int] = Body(None)
):
    """Update animation properties"""
    try:
        animation = await animation_service.update_animation(
            animation_id=animation_id,
            name=name,
            animation_type=animation_type,
            fps=fps
        )
        return animation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/frames/reorder", response_model=Dict[str, Any])
async def reorder_frames(
    animation_id: str = Body(..., description="ID of the animation"),
    frame_order: List[str] = Body(..., description="List of frame IDs in desired order")
):
    """Reorder animation frames"""
    try:
        animation = await animation_service.reorder_frames(
            animation_id=animation_id,
            frame_order=frame_order
        )
        return animation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/frames/{frame_id}", response_model=Dict[str, bool])
async def delete_frame(frame_id: str):
    """Delete a frame from an animation"""
    try:
        success = await animation_service.delete_frame(frame_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{animation_id}", response_model=Dict[str, bool])
async def delete_animation(animation_id: str):
    """Delete an animation and all its frames"""
    try:
        success = await animation_service.delete_animation(animation_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/spritesheet/{animation_id}", response_model=Dict[str, Any])
async def generate_spritesheet(animation_id: str):
    """Generate a spritesheet from animation frames"""
    try:
        spritesheet = await animation_service.generate_spritesheet(animation_id)
        return spritesheet
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 