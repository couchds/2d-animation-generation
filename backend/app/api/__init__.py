from fastapi import APIRouter
from .endpoints import sprite, animation

router = APIRouter()

router.include_router(sprite.router, prefix="/sprites", tags=["sprites"])
router.include_router(animation.router, prefix="/animations", tags=["animations"]) 