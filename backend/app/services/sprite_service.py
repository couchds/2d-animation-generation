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
            
            # Format datetime fields as strings
            if sprite.created_at:
                sprite.created_at = sprite.created_at.isoformat()
            if sprite.updated_at:
                sprite.updated_at = sprite.updated_at.isoformat()
                
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

    async def edit_sprite_image(self, sprite_id: str, prompt: str, num_variations: int = 5) -> List[Sprite]:
        try:
            logger.info("\n" + "="*80)
            logger.info("SPRITE EDIT STARTED")
            logger.info(f"Sprite ID: {sprite_id}")
            logger.info(f"Edit prompt: {prompt}")
            logger.info(f"Number of variations: {num_variations}")
            logger.info("="*80 + "\n")
            
            # Get the original sprite
            db = next(get_db())
            original_sprite = db.query(Sprite).filter(Sprite.id == sprite_id).first()
            
            if not original_sprite:
                raise Exception(f"Sprite with ID {sprite_id} not found")
            
            # Format the edit prompt
            edit_instructions = f"EDIT ONLY - DO NOT RECREATE: The reference image shows {original_sprite.description}. MAKE EXACTLY THESE CHANGES: {prompt}. DO NOT ALTER any other elements (proportions, colors, style, background transparency) unless specifically mentioned in the edit request. Preserve the existing art style and character identity exactly as shown in the reference image."
            formatted_prompt = await self.prompt_service.format_edit_prompt(edit_instructions)
            
            logger.info("\n" + "="*80)
            logger.info("EDITING IMAGE WITH GPT-IMAGE-1")
            logger.info(f"Using prompt: {formatted_prompt}")
            logger.info("="*80 + "\n")
            
            # List to store all variations
            variations = []
            
            try:
                # Download the original image if it's a URL
                logger.info("Starting image retrieval process...")
                original_image_path = None
                if original_sprite.url.startswith("http"):
                    logger.info(f"Downloading image from URL: {original_sprite.url}")
                    import requests
                    import tempfile
                    import os  # Import os here to ensure it's available in this scope
                    import time
                    
                    # Create a temporary file for the original image
                    original_image_fd, original_image_path = tempfile.mkstemp(suffix=".png")
                    logger.info(f"Created temporary file: {original_image_path}")
                    
                    # Retry parameters
                    max_retries = 3
                    retry_delay = 2
                    timeout = 30  # Increased timeout to 30 seconds
                    
                    # Try to download with retries
                    for retry in range(max_retries):
                        try:
                            logger.info(f"Download attempt {retry + 1}/{max_retries}")
                            
                            # If we're using localhost URLs, try to convert to a direct file path
                            if BACKEND_URL and original_sprite.url.startswith(BACKEND_URL) and "localhost" in BACKEND_URL:
                                logger.info("Detected localhost URL, attempting to use direct file access")
                                local_path = original_sprite.url.replace(f"{BACKEND_URL}/static/", "")
                                static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
                                direct_path = os.path.join(static_dir, local_path)
                                
                                if os.path.exists(direct_path):
                                    logger.info(f"Found local file at {direct_path}, copying directly")
                                    with open(direct_path, 'rb') as src, os.fdopen(original_image_fd, 'wb') as dst:
                                        dst.write(src.read())
                                    logger.info(f"Successfully copied local file to: {original_image_path}")
                                    break  # Exit retry loop on success
                                else:
                                    logger.warning(f"Local file not found at {direct_path}, falling back to HTTP")
                            
                            # Download via HTTP if direct access didn't work or wasn't possible
                            logger.info(f"Downloading via HTTP with {timeout}s timeout")
                            response = requests.get(original_sprite.url, stream=True, timeout=timeout)
                            logger.info(f"Download status code: {response.status_code}")
                            
                            if response.status_code == 200:
                                # Use the file descriptor to write the content
                                with os.fdopen(original_image_fd, 'wb') as f:
                                    # Set chunk size and use a counter for logging
                                    chunk_size = 8192
                                    chunks_downloaded = 0
                                    total_size = 0
                                    
                                    for chunk in response.iter_content(chunk_size=chunk_size):
                                        if chunk:  # filter out keep-alive chunks
                                            f.write(chunk)
                                            chunks_downloaded += 1
                                            total_size += len(chunk)
                                            # Log every 10 chunks to show progress
                                            if chunks_downloaded % 10 == 0:
                                                logger.info(f"Downloaded {chunks_downloaded} chunks ({total_size / 1024:.1f} KB)")
                                
                                logger.info(f"Downloaded original image to: {original_image_path}")
                                # Check if file was actually written
                                if os.path.getsize(original_image_path) > 0:
                                    logger.info(f"File size: {os.path.getsize(original_image_path)} bytes")
                                    break  # Exit retry loop on success
                                else:
                                    logger.error("Downloaded file is empty, will retry")
                                    if retry < max_retries - 1:  # Don't recreate file on last attempt
                                        os.remove(original_image_path)
                                        original_image_fd, original_image_path = tempfile.mkstemp(suffix=".png")
                                        logger.info(f"Created new temporary file: {original_image_path}")
                            else:
                                # Close file descriptor and remove file on error
                                os.remove(original_image_path)
                                raise Exception(f"Failed to download original image: HTTP {response.status_code}")
                                
                        except requests.exceptions.Timeout:
                            logger.error(f"Request timed out (attempt {retry + 1}/{max_retries})")
                            if retry < max_retries - 1:
                                logger.info(f"Waiting {retry_delay}s before retry...")
                                time.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                                
                                # Recreate the file for the next attempt
                                try:
                                    os.close(original_image_fd)  # Try to close, but it may already be closed
                                except:
                                    pass  # Ignore errors if already closed
                                
                                try:
                                    os.remove(original_image_path)
                                except:
                                    pass  # Ignore errors if file doesn't exist
                                    
                                original_image_fd, original_image_path = tempfile.mkstemp(suffix=".png")
                                logger.info(f"Created new temporary file: {original_image_path}")
                            else:
                                try:
                                    os.close(original_image_fd)  # Try to close, but it may already be closed
                                except:
                                    pass  # Ignore errors if already closed
                                
                                try:
                                    os.remove(original_image_path)
                                except:
                                    pass  # Ignore errors if file doesn't exist
                                    
                                raise Exception(f"Image download timed out after {max_retries} attempts")
                                
                        except (requests.exceptions.RequestException, Exception) as e:
                            # File descriptor management
                            try:
                                os.close(original_image_fd)  # Try to close, but it may already be closed
                            except:
                                pass  # Ignore errors if already closed
                            
                            try:
                                os.remove(original_image_path)
                            except:
                                pass  # Ignore errors if file doesn't exist
                                
                            # Log and re-raise
                            if isinstance(e, requests.exceptions.RequestException):
                                logger.error(f"Request error: {str(e)}")
                                raise Exception(f"Failed to download image: {str(e)}")
                            else:
                                logger.error(f"Unexpected error during download: {str(e)}")
                                raise Exception(f"Failed to download image: {str(e)}")
                else:
                    # If it's a local path (starts with /static/), get the absolute path
                    logger.info(f"Processing local image path: {original_sprite.url}")
                    
                    # Check if URL has the backend URL prefix and strip it if needed
                    image_path = original_sprite.url
                    if BACKEND_URL and image_path.startswith(BACKEND_URL):
                        image_path = image_path.replace(f"{BACKEND_URL}", "")
                    
                    if image_path.startswith("/static/"):
                        image_path = image_path.replace("/static/", "")
                    
                    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
                    original_image_path = os.path.join(static_dir, image_path)
                    
                    logger.info(f"Resolving to absolute path: {original_image_path}")
                    
                    if not os.path.exists(original_image_path):
                        logger.error(f"File not found: {original_image_path}")
                        logger.error(f"Static directory contents: {os.listdir(static_dir)}")
                        raise Exception(f"Original image file not found: {original_image_path}")
                    
                    logger.info(f"Using original image from: {original_image_path}")
                    logger.info(f"File size: {os.path.getsize(original_image_path)} bytes")
                
                # First, capture the alpha channel from the original image
                original_alpha = None
                try:
                    from PIL import Image
                    import numpy as np
                    import io
                    
                    # Load the original image to extract its alpha channel
                    with open(original_image_path, "rb") as orig_file:
                        orig_img = Image.open(orig_file)
                        if orig_img.mode == 'RGBA':
                            # Store the original alpha channel
                            logger.info("Capturing alpha channel from original image")
                            orig_img_array = np.array(orig_img)
                            original_alpha = orig_img_array[:, :, 3].copy()
                            original_size = orig_img.size
                            logger.info(f"Original image size: {original_size}")
                            logger.info(f"Original alpha channel shape: {original_alpha.shape}")
                except Exception as e:
                    logger.warning(f"Failed to capture original alpha channel: {str(e)}")
                    original_alpha = None
                
                # Generate multiple variations
                for i in range(num_variations):
                    logger.info(f"Generating variation {i+1}/{num_variations}")
                    
                    # Use OpenAI's images.edit endpoint with the original image
                    logger.info("Opening image file...")
                    # Open the file by path (not using file descriptor which may be closed)
                    with open(original_image_path, "rb") as image_file:
                        # Read the image data
                        image_data = image_file.read()
                        
                        logger.info("Preparing to call OpenAI images.edit API...")
                        logger.info(f"Image data length: {len(image_data)} bytes")
                        
                        # Create the edit API request
                        logger.info("Calling OpenAI API now...")
                        
                        # For gpt-image-1, reopen the file using the path
                        with open(original_image_path, "rb") as reopened_file:
                            response = openai.images.edit(
                                model="gpt-image-1",
                                image=reopened_file,  # Pass a freshly opened file object
                                prompt=formatted_prompt,
                                size="1024x1024"
                            )
                        
                        # Log information about the response
                        logger.info("OpenAI API call successful")
                        logger.info(f"Response contains {len(response.data)} images")
                    
                    # Log successful completion of the API call
                    logger.info("Successfully received response from OpenAI images.edit API")
                    
                    # Get base64 image data
                    image_base64 = response.data[0].b64_json
                    logger.info(f"Received base64 image data with length: {len(image_base64)}")
                    
                    # Post-process the image to restore original transparency...
                    logger.info("Post-processing image to restore original transparency...")
                    try:
                        # Import PIL for image processing
                        from PIL import Image
                        import io
                        import numpy as np
                        
                        # Decode the base64 image
                        image_data = base64.b64decode(image_base64)
                        
                        # Open the image with PIL
                        edited_img = Image.open(io.BytesIO(image_data))
                        
                        # Convert to RGBA if not already
                        if edited_img.mode != 'RGBA':
                            edited_img = edited_img.convert('RGBA')
                        
                        # If we have the original alpha channel, apply it to the edited image
                        if original_alpha is not None:
                            logger.info("Applying original alpha channel to edited image")
                            
                            # Resize edited image to match original if needed
                            if edited_img.size != original_size:
                                logger.info(f"Resizing edited image from {edited_img.size} to {original_size}")
                                edited_img = edited_img.resize(original_size, Image.LANCZOS)
                            
                            # Get the pixel data as a numpy array
                            edited_array = np.array(edited_img)
                            
                            # Apply the original alpha channel
                            edited_array[:, :, 3] = original_alpha
                            
                            # Convert back to an image
                            edited_img = Image.fromarray(edited_array)
                            logger.info("Successfully restored original transparency")
                        else:
                            # Fallback to the black background removal approach
                            logger.info("No original alpha channel available, using black background removal")
                            
                            # Get the pixel data as a numpy array
                            pixel_data = np.array(edited_img)
                            
                            # Identify black or near-black pixels and make them transparent
                            r, g, b, a = pixel_data[:,:,0], pixel_data[:,:,1], pixel_data[:,:,2], pixel_data[:,:,3]
                            
                            # Find dark pixels (threshold can be adjusted)
                            mask = (r < 10) & (g < 10) & (b < 10)
                            
                            # Only consider pixels near the edges as potential background
                            h, w = mask.shape
                            y, x = np.ogrid[:h, :w]
                            edge_dist = np.minimum(np.minimum(x, w-1-x), np.minimum(y, h-1-y))
                            
                            # Only apply to pixels that are near edges
                            edge_mask = edge_dist < 5  # Pixels within 5 pixels of the edge
                            
                            # Start by making edge black pixels transparent
                            initial_transparency = mask & edge_mask
                            pixel_data[initial_transparency, 3] = 0
                            
                            try:
                                # Use flood fill to find connected black regions
                                from scipy import ndimage
                                
                                # Find connected black regions that touch transparent pixels
                                transparent_mask = (pixel_data[:,:,3] == 0)
                                structure = ndimage.generate_binary_structure(2, 2)
                                
                                # Dilate the transparent mask slightly
                                dilated_mask = ndimage.binary_dilation(transparent_mask, structure, iterations=1)
                                
                                # Identify dark pixels connected to transparent areas
                                connected_dark = mask & dilated_mask
                                
                                # Repeat several times to expand inward
                                for _ in range(10):
                                    pixel_data[connected_dark, 3] = 0
                                    transparent_mask = (pixel_data[:,:,3] == 0)
                                    dilated_mask = ndimage.binary_dilation(transparent_mask, structure, iterations=1)
                                    connected_dark = mask & dilated_mask
                                    if not np.any(connected_dark):
                                        break
                                        
                                edited_img = Image.fromarray(pixel_data)
                                logger.info("Successfully applied black background removal")
                            except ImportError:
                                logger.warning("scipy not available, using simple edge-based transparency only")
                        
                        # Save to a buffer
                        buffer = io.BytesIO()
                        edited_img.save(buffer, format="PNG")
                        buffer.seek(0)
                        
                        # Convert back to base64
                        processed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        
                        # Use the processed image
                        image_base64 = processed_base64
                        logger.info("Post-processing complete")
                        
                    except Exception as e:
                        logger.warning(f"Error in transparency post-processing: {str(e)}")
                        logger.warning("Using original image without transparency correction")
                    
                    # Save the image to a file in the static directory
                    image_filename = f"{uuid.uuid4()}.png"
                    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
                    
                    # Create static directory if it doesn't exist
                    os.makedirs(static_dir, exist_ok=True)
                    
                    image_path = os.path.join(static_dir, image_filename)
                    logger.info(f"Saving edited image to: {image_path}")
                    
                    with open(image_path, "wb") as f:
                        f.write(base64.b64decode(image_base64))
                    
                    # Create full URL for the image with domain
                    image_url = f"{BACKEND_URL}/static/{image_filename}"
                    
                    logger.info("Edited image generated successfully")
                    logger.info(f"Image saved to: {image_path}")
                    logger.info(f"Image URL: {image_url}")
                    
                    # Create sprite record with edited image, including parent relationship
                    variation_sprite = Sprite(
                        id=str(uuid.uuid4()),
                        url=image_url,
                        description=original_sprite.description,  # Keep original description
                        edit_description=prompt,  # Add the edit description
                        parent_id=original_sprite.id,  # Link to parent sprite
                        is_base_image=False  # Mark as not a base image initially
                    )
                    
                    # Save to database
                    logger.info(f"Saving edited sprite variation {i+1} to database...")
                    db.add(variation_sprite)
                    db.commit()
                    db.refresh(variation_sprite)
                    
                    # Format datetime fields as strings
                    if variation_sprite.created_at:
                        variation_sprite.created_at = variation_sprite.created_at.isoformat()
                    if variation_sprite.updated_at:
                        variation_sprite.updated_at = variation_sprite.updated_at.isoformat()
                        
                    logger.info(f"Edited sprite variation {i+1} saved with ID: {variation_sprite.id}")
                    
                    # Add to the list of variations
                    variations.append(variation_sprite)
                
                # Clean up temporary file if created
                if original_sprite.url.startswith("http"):
                    try:
                        os.remove(original_image_path)
                    except:
                        pass  # Ignore errors
                    logger.info(f"Cleaned up temporary file: {original_image_path}")
                    
                logger.info("\n" + "="*80)
                logger.info(f"SPRITE EDIT COMPLETE - Generated {len(variations)} variations")
                logger.info("="*80 + "\n")
                
                # Convert sprites to dictionaries to ensure proper serialization
                serialized_variations = []
                for sprite in variations:
                    serialized_sprite = {
                        "id": sprite.id,
                        "url": sprite.url,
                        "description": sprite.description,
                        "parent_id": sprite.parent_id,
                        "edit_description": sprite.edit_description,
                        "is_base_image": sprite.is_base_image,
                        "created_at": sprite.created_at if isinstance(sprite.created_at, str) else (sprite.created_at.isoformat() if sprite.created_at else None),
                        "updated_at": sprite.updated_at if isinstance(sprite.updated_at, str) else (sprite.updated_at.isoformat() if sprite.updated_at else None)
                    }
                    serialized_variations.append(serialized_sprite)
                
                return serialized_variations
                
            except Exception as e:
                logger.error("\n" + "="*80)
                logger.error("SPRITE EDIT FAILED")
                logger.error(f"Error in edit_sprite_image: {str(e)}", exc_info=True)
                logger.error("="*80 + "\n")
                raise Exception(f"Failed to edit sprite: {str(e)}")
        except Exception as e:
            logger.error("\n" + "="*80)
            logger.error("SPRITE EDIT FAILED")
            logger.error(f"Error in edit_sprite_image outer block: {str(e)}", exc_info=True)
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
            
            # Convert all Sprite objects to dictionaries for serialization
            def sprite_to_dict(sprite):
                sprite_dict = {
                    "id": sprite.id,
                    "url": sprite.url,
                    "description": sprite.description,
                    "parent_id": sprite.parent_id,
                    "edit_description": sprite.edit_description,
                    "is_base_image": sprite.is_base_image,
                    "created_at": sprite.created_at.isoformat() if sprite.created_at else None,
                    "updated_at": sprite.updated_at.isoformat() if sprite.updated_at else None
                }
                return sprite_dict
            
            # Convert all objects to dictionaries
            current_dict = sprite_to_dict(current_sprite)
            ancestors_dicts = [sprite_to_dict(sprite) for sprite in ancestors]
            children_dicts = [sprite_to_dict(sprite) for sprite in children]
            timeline_dicts = [sprite_to_dict(sprite) for sprite in timeline]
            
            return {
                "current": current_dict,
                "ancestors": ancestors_dicts,
                "children": children_dicts,
                "timeline": timeline_dicts
            }
        except Exception as e:
            logger.error(f"Error in get_sprite_history: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get sprite history: {str(e)}") 