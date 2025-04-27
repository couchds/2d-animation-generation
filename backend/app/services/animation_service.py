import os
import uuid
import logging
from typing import List, Dict, Any, Optional
import openai
import base64
from PIL import Image
import io
import tempfile
from sqlalchemy import desc
import requests
from sqlalchemy.orm import Session

from ..models.animation import Animation, Frame
from ..models.sprite import Sprite
from ..utils.database import get_db
from .sprite_service import SpriteService
from ..schemas.animation import AnimationCreate, AnimationUpdate, FrameCreate
from ..constants import BACKEND_URL

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI with API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class AnimationService:
    def __init__(self):
        self.sprite_service = SpriteService()
    
    async def create_animation(self, name: str, base_sprite_id: str, animation_type: Optional[str] = None, fps: int = 12) -> Animation:
        """
        Create a new animation for a sprite.
        
        Args:
            name: The name of the animation
            base_sprite_id: The ID of the base sprite
            animation_type: Optional type of animation (walk, run, idle, etc.)
            fps: Frames per second for playback
            
        Returns:
            The created Animation object
        """
        try:
            logger.info(f"Creating new animation named '{name}' for sprite {base_sprite_id}")
            
            # Get the database session
            db = next(get_db())
            
            # Get base sprite to verify it exists
            base_sprite = db.query(Sprite).filter(Sprite.id == base_sprite_id).first()
            if not base_sprite:
                raise Exception(f"Base sprite with ID {base_sprite_id} not found")
                
            # Create the animation
            animation = Animation(
                id=str(uuid.uuid4()),
                name=name,
                base_sprite_id=base_sprite_id,
                animation_type=animation_type,
                fps=fps
            )
            
            # Save to database
            db.add(animation)
            db.commit()
            db.refresh(animation)
            
            logger.info(f"Created animation with ID {animation.id}")
            return animation
            
        except Exception as e:
            logger.error(f"Error creating animation: {str(e)}")
            raise Exception(f"Failed to create animation: {str(e)}")
    
    async def generate_frame(self, animation_id: str, prompt: str, order: Optional[int] = None) -> Frame:
        """
        Generate a new frame for an animation using AI, based on editing the original sprite.
        
        Args:
            animation_id: The ID of the animation
            prompt: The description for generating this frame
            order: Optional position in the sequence (if None, appends to the end)
            
        Returns:
            The created Frame object
        """
        try:
            logger.info(f"Generating new frame for animation {animation_id}")
            logger.info(f"Frame generation prompt: {prompt}")
            
            # Get the database session
            db = next(get_db())
            
            # Get the animation to verify it exists
            animation = db.query(Animation).filter(Animation.id == animation_id).first()
            if not animation:
                raise Exception(f"Animation with ID {animation_id} not found")
                
            # Get the base sprite
            base_sprite = db.query(Sprite).filter(Sprite.id == animation.base_sprite_id).first()
            if not base_sprite:
                raise Exception(f"Base sprite with ID {animation.base_sprite_id} not found")
            
            # If order is not specified, put it at the end
            if order is None:
                # Count existing frames
                frame_count = db.query(Frame).filter(Frame.animation_id == animation_id).count()
                order = frame_count
            
            # Generate the frame image using OpenAI
            try:
                # Format edit prompt to maintain character consistency
                edit_instructions = f"EDIT ONLY - DO NOT RECREATE: The reference image shows {base_sprite.description}. MAKE EXACTLY THESE CHANGES FOR ANIMATION: {prompt}. Maintain the exact same art style, colors, and character details. Only change the pose/position as needed for the animation frame."
                
                # Download the original sprite image
                original_image_path = None
                temp_file = None
                
                # Get the sprite image
                if base_sprite.url.startswith("http"):
                    logger.info(f"Downloading image from URL: {base_sprite.url}")
                    
                    # If it's a localhost URL, try to resolve it locally first
                    if BACKEND_URL in base_sprite.url:
                        # Extract the path from the URL
                        local_path = base_sprite.url.replace(f"{BACKEND_URL}/static/", "")
                        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
                        file_path = os.path.join(static_dir, local_path)
                        
                        # Check if the file exists locally
                        if os.path.exists(file_path):
                            logger.info(f"Found local file for URL: {file_path}")
                            original_image_path = file_path
                        else:
                            logger.warning(f"Could not find local file for URL: {base_sprite.url}, will try HTTP request")
                    
                    # If not a localhost URL or local file not found, proceed with HTTP request
                    if not original_image_path:
                        # Create a temporary file for the original image
                        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                        original_image_path = temp_file.name
                        temp_file.close()  # Close the file but keep the name
                        
                        # Download the image with increased timeout
                        try:
                            response = requests.get(base_sprite.url, timeout=60)
                            
                            if response.status_code == 200:
                                with open(original_image_path, 'wb') as f:
                                    f.write(response.content)
                                logger.info(f"Downloaded original sprite to: {original_image_path}")
                            else:
                                raise Exception(f"Failed to download original sprite: HTTP {response.status_code}")
                        except requests.exceptions.Timeout:
                            logger.error(f"Timeout while downloading image from {base_sprite.url}")
                            raise Exception(f"Image download timed out. Please ensure the server at {BACKEND_URL} is running properly.")
                        except requests.exceptions.ConnectionError:
                            logger.error(f"Connection error while downloading image from {base_sprite.url}")
                            raise Exception(f"Connection error. Please ensure the server at {BACKEND_URL} is running and accessible.")
                else:
                    # If it's a local path (starts with /static/), get the absolute path
                    logger.info(f"Processing local image path: {base_sprite.url}")
                    
                    # Check if URL has the backend URL prefix and strip it if needed
                    image_path = base_sprite.url
                    if BACKEND_URL and image_path.startswith(BACKEND_URL):
                        image_path = image_path.replace(f"{BACKEND_URL}", "")
                    
                    if image_path.startswith("/static/"):
                        image_path = image_path.replace("/static/", "")
                    
                    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
                    original_image_path = os.path.join(static_dir, image_path)
                    
                    if not os.path.exists(original_image_path):
                        raise Exception(f"Original sprite file not found: {original_image_path}")
                    
                    logger.info(f"Using original sprite from: {original_image_path}")
                
                # Open and read the image as bytes
                with open(original_image_path, "rb") as image_file:
                    image_data = image_file.read()
                
                # Create a mask with full transparency (fully editable)
                from PIL import Image
                import io
                
                # Create a completely white mask at the same size as the original image
                with Image.open(original_image_path) as img:
                    width, height = img.size
                    mask = Image.new("RGBA", (width, height), (255, 255, 255, 255))
                    
                    # Convert to bytes
                    mask_bytes = io.BytesIO()
                    mask.save(mask_bytes, format="PNG")
                    mask_bytes = mask_bytes.getvalue()
                
                # Generate the frame using OpenAI image edit
                logger.info("Calling OpenAI API for frame generation...")
                
                # For gpt-image-1, reopen the file using the path
                with open(original_image_path, "rb") as reopened_file:
                    response = openai.images.edit(
                        model="gpt-image-1",
                        image=reopened_file,  # Pass a freshly opened file object
                        prompt=edit_instructions,
                        size="1024x1024"
                    )
                
                # Get the image URL or base64 data
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
                
                logger.info(f"Generated frame image: {image_url}")
                
                # Clean up the temporary file if we created one
                if temp_file and os.path.exists(original_image_path):
                    os.unlink(original_image_path)
                    
            except Exception as e:
                logger.error(f"Error generating frame image: {str(e)}")
                # Clean up the temporary file if an error occurred
                if temp_file and original_image_path and os.path.exists(original_image_path):
                    os.unlink(original_image_path)
                raise Exception(f"Failed to generate frame image: {str(e)}")
                
            # Create the frame
            frame = Frame(
                id=str(uuid.uuid4()),
                animation_id=animation_id,
                url=image_url,
                order=order,
                prompt=prompt
            )
            
            # Save to database
            db.add(frame)
            db.commit()
            db.refresh(frame)
            
            logger.info(f"Created frame with ID {frame.id} at position {order}")
            return frame
            
        except Exception as e:
            logger.error(f"Error generating frame: {str(e)}")
            raise Exception(f"Failed to generate frame: {str(e)}")
    
    async def get_animation(self, animation_id: str) -> Dict[str, Any]:
        """Get animation details with its frames"""
        try:
            db = next(get_db())
            animation = db.query(Animation).filter(Animation.id == animation_id).first()
            
            if not animation:
                return None
                
            # Get all frames in order
            frames = db.query(Frame).filter(
                Frame.animation_id == animation_id
            ).order_by(Frame.order).all()
            
            # Format response
            result = {
                "id": animation.id,
                "name": animation.name,
                "base_sprite_id": animation.base_sprite_id,
                "animation_type": animation.animation_type,
                "fps": animation.fps,
                "created_at": animation.created_at.isoformat() if animation.created_at else None,
                "updated_at": animation.updated_at.isoformat() if animation.updated_at else None,
                "frames": [
                    {
                        "id": frame.id,
                        "url": frame.url,
                        "order": frame.order,
                        "prompt": frame.prompt,
                        "created_at": frame.created_at.isoformat() if frame.created_at else None
                    }
                    for frame in frames
                ]
            }
            
            return result
        except Exception as e:
            logger.error(f"Error getting animation: {str(e)}")
            raise Exception(f"Failed to get animation: {str(e)}")

    async def get_sprite_animations(self, sprite_id: str) -> List[Dict[str, Any]]:
        """Get all animations for a sprite"""
        try:
            db = next(get_db())
            animations = db.query(Animation).filter(
                Animation.base_sprite_id == sprite_id
            ).order_by(desc(Animation.created_at)).all()
            
            results = []
            for animation in animations:
                # Get frame count
                frame_count = db.query(Frame).filter(
                    Frame.animation_id == animation.id
                ).count()
                
                results.append({
                    "id": animation.id,
                    "name": animation.name,
                    "base_sprite_id": animation.base_sprite_id,
                    "animation_type": animation.animation_type,
                    "fps": animation.fps,
                    "frame_count": frame_count,
                    "created_at": animation.created_at.isoformat() if animation.created_at else None,
                    "updated_at": animation.updated_at.isoformat() if animation.updated_at else None
                })
                
            return results
        except Exception as e:
            logger.error(f"Error getting sprite animations: {str(e)}")
            raise Exception(f"Failed to get sprite animations: {str(e)}")
            
    async def update_animation(self, animation_id: str, name: Optional[str] = None, 
                            animation_type: Optional[str] = None, fps: Optional[int] = None) -> Dict[str, Any]:
        """Update animation properties"""
        try:
            db = next(get_db())
            animation = db.query(Animation).filter(Animation.id == animation_id).first()
            
            if not animation:
                raise Exception(f"Animation with ID {animation_id} not found")
                
            # Update fields if provided
            if name is not None:
                animation.name = name
            if animation_type is not None:
                animation.animation_type = animation_type
            if fps is not None:
                animation.fps = fps
                
            db.commit()
            db.refresh(animation)
            
            # Return the updated animation
            return await self.get_animation(animation_id)
        except Exception as e:
            logger.error(f"Error updating animation: {str(e)}")
            raise Exception(f"Failed to update animation: {str(e)}")
            
    async def delete_animation(self, animation_id: str) -> bool:
        """Delete an animation and its frames"""
        try:
            db = next(get_db())
            animation = db.query(Animation).filter(Animation.id == animation_id).first()
            
            if not animation:
                return False
                
            # Delete the animation (frames will be cascade deleted)
            db.delete(animation)
            db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting animation: {str(e)}")
            raise Exception(f"Failed to delete animation: {str(e)}")
            
    async def reorder_frames(self, animation_id: str, frame_order: List[str]) -> Dict[str, Any]:
        """
        Reorder animation frames
        
        Args:
            animation_id: The animation ID
            frame_order: List of frame IDs in the desired order
            
        Returns:
            The updated animation with frames
        """
        try:
            db = next(get_db())
            
            # Verify animation exists
            animation = db.query(Animation).filter(Animation.id == animation_id).first()
            if not animation:
                raise Exception(f"Animation with ID {animation_id} not found")
                
            # Get existing frames
            existing_frames = db.query(Frame).filter(
                Frame.animation_id == animation_id
            ).all()
            
            # Create a map of frame ID to frame object
            frame_map = {frame.id: frame for frame in existing_frames}
            
            # Verify all frame IDs are valid
            for frame_id in frame_order:
                if frame_id not in frame_map:
                    raise Exception(f"Frame with ID {frame_id} not found in animation {animation_id}")
            
            # Update order based on the provided list
            for i, frame_id in enumerate(frame_order):
                frame_map[frame_id].order = i
                
            db.commit()
            
            # Return the updated animation
            return await self.get_animation(animation_id)
        except Exception as e:
            logger.error(f"Error reordering frames: {str(e)}")
            raise Exception(f"Failed to reorder frames: {str(e)}")
            
    async def delete_frame(self, frame_id: str) -> bool:
        """Delete a specific frame"""
        try:
            db = next(get_db())
            frame = db.query(Frame).filter(Frame.id == frame_id).first()
            
            if not frame:
                return False
                
            # Store animation ID and current order for reordering
            animation_id = frame.animation_id
            deleted_order = frame.order
            
            # Delete the frame
            db.delete(frame)
            
            # Update order of remaining frames
            remaining_frames = db.query(Frame).filter(
                Frame.animation_id == animation_id,
                Frame.order > deleted_order
            ).all()
            
            for frame in remaining_frames:
                frame.order -= 1
                
            db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting frame: {str(e)}")
            raise Exception(f"Failed to delete frame: {str(e)}")
            
    async def generate_animation_preset(self, animation_id: str, preset_type: str, num_frames: int = 4) -> List[Frame]:
        """
        Generate multiple frames based on a preset animation type
        
        Args:
            animation_id: The animation ID
            preset_type: Type of animation (walk, run, idle, jump, etc.)
            num_frames: Number of frames to generate (default 4)
            
        Returns:
            List of created frames
        """
        try:
            db = next(get_db())
            
            # Verify animation exists
            animation = db.query(Animation).filter(Animation.id == animation_id).first()
            if not animation:
                raise Exception(f"Animation with ID {animation_id} not found")
                
            # Get base sprite
            base_sprite = db.query(Sprite).filter(Sprite.id == animation.base_sprite_id).first()
            if not base_sprite:
                raise Exception(f"Base sprite with ID {animation.base_sprite_id} not found")
                
            # Update animation type
            animation.animation_type = preset_type
            db.commit()
            
            # Define frame descriptions based on preset type
            frame_descriptions = []
            character_desc = base_sprite.description
            
            if preset_type == "idle":
                # Base idle animation frames - we'll use as many as requested up to this number
                base_idle_frames = [
                    f"{character_desc} standing in neutral pose, completely still, looking exactly like the original sprite",
                    f"{character_desc} in neutral pose with slight breathing motion, subtle movement but maintaining exact design",
                    f"{character_desc} in neutral pose with slight head movement, keeping all design details consistent",
                    f"{character_desc} with subtle blinking or small gesture, maintaining character design",
                    f"{character_desc} with minimal weight shift, keeping exact style and colors",
                    f"{character_desc} returning to completely still position, identical to original sprite design"
                ]
                
                # Use the requested number of frames, but don't exceed what we have defined
                max_frames = min(num_frames, len(base_idle_frames))
                frame_descriptions = base_idle_frames[:max_frames]
                
                # If we need more frames than are defined, repeat the cycle
                while len(frame_descriptions) < num_frames:
                    remaining = num_frames - len(frame_descriptions)
                    frame_descriptions.extend(base_idle_frames[:remaining])
            elif preset_type == "walk":
                # Base walk animation frames
                base_walk_frames = [
                    f"{character_desc} with left foot forward, right foot back in walking position, same design as original sprite",
                    f"{character_desc} with feet passing each other in mid-step, maintaining exact design details",
                    f"{character_desc} with right foot forward, left foot back in walking position, consistent with original sprite",
                    f"{character_desc} with feet passing each other in mid-step, returning to first position, identical proportions"
                ]
                
                # Use the requested number of frames
                max_frames = min(num_frames, len(base_walk_frames))
                frame_descriptions = base_walk_frames[:max_frames]
                
                # If we need more frames than are defined, repeat the cycle
                while len(frame_descriptions) < num_frames:
                    remaining = num_frames - len(frame_descriptions)
                    frame_descriptions.extend(base_walk_frames[:remaining])
                
            elif preset_type == "run":
                # Base run animation frames
                base_run_frames = [
                    f"{character_desc} in running pose with right leg forward, left leg back, arms in opposite position, same design",
                    f"{character_desc} in mid-air running pose, legs tucked slightly, maintaining exact character design",
                    f"{character_desc} in running pose with left leg forward, right leg back, arms in opposite position, consistent colors",
                    f"{character_desc} in mid-air running pose, legs tucked slightly, returning to first position, identical style"
                ]
                
                # Use the requested number of frames
                max_frames = min(num_frames, len(base_run_frames))
                frame_descriptions = base_run_frames[:max_frames]
                
                # If we need more frames than are defined, repeat the cycle
                while len(frame_descriptions) < num_frames:
                    remaining = num_frames - len(frame_descriptions)
                    frame_descriptions.extend(base_run_frames[:remaining])
                
            elif preset_type == "jump":
                # Base jump animation frames
                base_jump_frames = [
                    f"{character_desc} in pre-jump crouching position, maintaining exact design details",
                    f"{character_desc} pushing off ground, beginning to rise, same design as original sprite",
                    f"{character_desc} in mid-air at peak of jump, limbs extended, consistent with original sprite",
                    f"{character_desc} beginning to fall from jump, maintaining same character design",
                    f"{character_desc} landing with bent knees to absorb impact, identical proportions and style",
                    f"{character_desc} returning to neutral standing position, matching original design perfectly"
                ]
                
                # Use the requested number of frames
                max_frames = min(num_frames, len(base_jump_frames))
                frame_descriptions = base_jump_frames[:max_frames]
                
                # If we need more frames than are defined, repeat the cycle
                while len(frame_descriptions) < num_frames:
                    remaining = num_frames - len(frame_descriptions)
                    frame_descriptions.extend(base_jump_frames[:remaining])
                
            else:
                # Generic animation for unknown types
                base_generic_frames = [
                    f"{character_desc} in {preset_type} animation, frame 1, matching original sprite design exactly", 
                    f"{character_desc} in {preset_type} animation, frame 2, consistent with original design",
                    f"{character_desc} in {preset_type} animation, frame 3, maintaining exact character design", 
                    f"{character_desc} in {preset_type} animation, frame 4, identical style and proportions"
                ]
                
                # Generate more frames if needed by creating descriptive variations
                if num_frames > 4:
                    for i in range(5, num_frames + 1):
                        base_generic_frames.append(
                            f"{character_desc} in {preset_type} animation, frame {i}, maintaining consistent style and design"
                        )
                
                # Use the requested number of frames
                frame_descriptions = base_generic_frames[:num_frames]
                
            # Generate frames
            created_frames = []
            for i, description in enumerate(frame_descriptions):
                frame = await self.generate_frame(
                    animation_id=animation_id,
                    prompt=description,
                    order=i
                )
                created_frames.append(frame)
                
            return created_frames
        except Exception as e:
            logger.error(f"Error generating preset animation: {str(e)}")
            raise Exception(f"Failed to generate preset animation: {str(e)}")
            
    async def generate_spritesheet(self, animation_id: str) -> Dict[str, Any]:
        """
        Generate a spritesheet from animation frames
        
        Args:
            animation_id: The animation ID
            
        Returns:
            Dictionary with the URL of the generated spritesheet and metadata
        """
        try:
            # Get animation and frames
            animation_data = await self.get_animation(animation_id)
            if not animation_data:
                raise Exception(f"Animation with ID {animation_id} not found")
                
            frames = animation_data.get("frames", [])
            if not frames:
                raise Exception(f"Animation has no frames")
                
            # Parameters for the spritesheet
            num_frames = len(frames)
            rows = 1
            cols = num_frames
            
            # If there are more than 10 frames, organize in a grid
            if num_frames > 10:
                rows = int(num_frames ** 0.5)  # Square root for balanced grid
                cols = (num_frames + rows - 1) // rows  # Ceiling division
                
            # Download all frame images
            frame_images = []
            for frame in frames:
                frame_url = frame["url"]
                
                # Handle absolute URLs
                if frame_url.startswith("http"):
                    # If it's a localhost URL, try to resolve it locally first
                    if BACKEND_URL in frame_url:
                        # Extract the path from the URL
                        local_path = frame_url.replace(f"{BACKEND_URL}/static/", "")
                        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
                        file_path = os.path.join(static_dir, local_path)
                        
                        # Check if the file exists locally
                        if os.path.exists(file_path):
                            logger.info(f"Found local file for URL: {file_path}")
                            frame_img = Image.open(file_path)
                            frame_images.append(frame_img)
                            continue  # Skip the HTTP request
                        else:
                            logger.warning(f"Could not find local file for URL: {frame_url}, will try HTTP request")
                    
                    # If not a localhost URL or local file not found, proceed with HTTP request
                    try:
                        response = requests.get(frame_url, timeout=60)
                        if response.status_code == 200:
                            frame_img = Image.open(io.BytesIO(response.content))
                            frame_images.append(frame_img)
                        else:
                            raise Exception(f"Failed to download frame image: HTTP {response.status_code} for {frame_url}")
                    except requests.exceptions.Timeout:
                        logger.error(f"Timeout while downloading frame image from {frame_url}")
                        raise Exception(f"Image download timed out. Please ensure the server at {BACKEND_URL} is running properly.")
                    except requests.exceptions.ConnectionError:
                        logger.error(f"Connection error while downloading frame image from {frame_url}")
                        raise Exception(f"Connection error. Please ensure the server at {BACKEND_URL} is running and accessible.")
                else:
                    # Handle local files
                    if frame_url.startswith("/static/"):
                        frame_path = frame_url.replace("/static/", "")
                        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
                        frame_path = os.path.join(static_dir, frame_path)
                        frame_img = Image.open(frame_path)
                        frame_images.append(frame_img)
                    else:
                        raise Exception(f"Unsupported frame URL format: {frame_url}")
            
            # Determine the frame size (assume all frames are the same size)
            if not frame_images:
                raise Exception("Failed to load any frame images")
                
            frame_width, frame_height = frame_images[0].size
            
            # Create the spritesheet
            spritesheet_width = frame_width * cols
            spritesheet_height = frame_height * rows
            spritesheet = Image.new('RGBA', (spritesheet_width, spritesheet_height), (0, 0, 0, 0))
            
            # Place each frame in the spritesheet
            for i, frame_img in enumerate(frame_images):
                row = i // cols
                col = i % cols
                x = col * frame_width
                y = row * frame_height
                spritesheet.paste(frame_img, (x, y))
                
            # Save the spritesheet
            sheet_filename = f"spritesheet_{animation_id}.png"
            static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
            sheet_path = os.path.join(static_dir, sheet_filename)
            spritesheet.save(sheet_path, format="PNG")
            
            # Create URL for the spritesheet
            sheet_url = f"{BACKEND_URL}/static/{sheet_filename}"
            
            # Return the spritesheet info
            return {
                "url": sheet_url,
                "frames": num_frames,
                "rows": rows,
                "cols": cols,
                "frame_width": frame_width,
                "frame_height": frame_height,
                "total_width": spritesheet_width,
                "total_height": spritesheet_height
            }
        except Exception as e:
            logger.error(f"Error generating spritesheet: {str(e)}")
            raise Exception(f"Failed to generate spritesheet: {str(e)}") 