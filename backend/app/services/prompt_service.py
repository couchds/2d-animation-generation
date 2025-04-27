import openai
import os
import logging

logger = logging.getLogger(__name__)

class PromptService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    async def format_sprite_prompt(self, user_prompt: str) -> str:
        try:
            logger.info("="*50)
            logger.info("PROMPT FORMATTING STARTED")
            logger.info(f"Original user prompt: {user_prompt}")
            
            system_prompt = """You are a professional 2D pixel art character designer for video games. 
            Your task is to enhance the user's description into a detailed prompt for generating a 2D pixel art character sprite.
            
            The enhanced prompt should:
            1. Specify "single character" to ensure only one character is generated
            2. Use "clean pixel art" style with no grid lines or rulers
            3. Include specific details about the character's appearance, colors, and features
            4. Specify the character should be in a neutral, centered pose suitable as a base for animations
            5. Emphasize that the background must be completely transparent (alpha channel)
            6. Specify the character should be isolated and centered in the frame with proper padding
            7. Keep the original character concept while adding necessary details
            
            Format the response as a single, detailed prompt sentence."""

            logger.info("Sending prompt to GPT for enhancement...")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a detailed prompt for this character: {user_prompt}"}
                ],
                temperature=0.7,
                max_tokens=150
            )

            formatted_prompt = response.choices[0].message.content.strip()
            
            # Add additional requirements to ensure the sprite is suitable for animation
            final_prompt = f"Create a single character: {formatted_prompt} The image must have a completely transparent background (alpha channel) with no ground, shadow, grid lines, rulers, or any other background elements. The character should be perfectly centered in the frame with equal padding on all sides (at least 10% of the image size). Clean, clear pixel art style suitable for animation frames. Ensure the entire character is visible with no clipping. No grid lines or rulers should be visible."
            
            logger.info("="*50)
            logger.info("PROMPT FORMATTING COMPLETE")
            logger.info(f"Formatted prompt: {final_prompt}")
            logger.info("="*50)
            return final_prompt

        except Exception as e:
            logger.error("="*50)
            logger.error("PROMPT FORMATTING FAILED")
            logger.error(f"Error formatting prompt: {str(e)}", exc_info=True)
            logger.error("Using fallback prompt")
            logger.error("="*50)
            # Fallback to a basic formatted prompt if the API call fails
            return f"Create a single character: a clean 2D pixel art character sprite for animation based on: {user_prompt}. The sprite should be in a clear pixel art style with a completely transparent background (alpha channel). The character should be centered in the frame with equal padding on all sides (at least 10% of the image size), in a neutral pose suitable as a base for animations, and isolated from any background elements. No ground, shadow, grid lines, rulers, or extra space around the character. Ensure the entire character is visible with no clipping."

    async def format_edit_prompt(self, edit_instructions: str) -> str:
        """
        Format a prompt specifically for editing sprites, without adding creation instructions.
        This method preserves the edit instructions exactly as provided without wrapping them
        in creation-focused language.
        
        Args:
            edit_instructions (str): The edit instructions to format
            
        Returns:
            str: The formatted edit prompt
        """
        logger.info("="*50)
        logger.info("EDIT PROMPT FORMATTING")
        logger.info(f"Original edit instructions: {edit_instructions}")
        
        # For edit prompts, we just return the instructions exactly as given
        # without adding any sprite creation boilerplate
        
        logger.info("="*50)
        logger.info("EDIT PROMPT FORMATTING COMPLETE")
        logger.info(f"Formatted edit prompt: {edit_instructions}")
        logger.info("="*50)
        
        return edit_instructions 