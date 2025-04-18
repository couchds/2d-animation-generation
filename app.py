import os
import streamlit as st
from PIL import Image
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize session state
if 'base_sprite' not in st.session_state:
    st.session_state.base_sprite = None
if 'animations' not in st.session_state:
    st.session_state.animations = {}

def generate_base_sprite(prompt):
    """Generate a base sprite using OpenAI's DALL-E"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Create a 2D sprite for a character based on this description: {prompt}. The sprite should be in a simple, clean style suitable for a 2D game.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Error generating sprite: {str(e)}")
        return None

def generate_animation_variation(base_prompt, animation_type):
    """Generate variations for different animations"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Create a {animation_type} animation frame for this character: {base_prompt}. The sprite should maintain the same style and proportions as the base sprite.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Error generating animation: {str(e)}")
        return None

def main():
    st.title("2D Animation Generator")
    
    # Base sprite generation
    st.header("1. Generate Base Sprite")
    base_prompt = st.text_input("Describe your character:")
    
    if st.button("Generate Base Sprite"):
        with st.spinner("Generating base sprite..."):
            sprite_url = generate_base_sprite(base_prompt)
            if sprite_url:
                st.session_state.base_sprite = sprite_url
                st.image(sprite_url, caption="Base Sprite")
    
    # Animation generation
    if st.session_state.base_sprite:
        st.header("2. Generate Animations")
        animation_types = ["idle", "walk", "run", "jump", "attack"]
        selected_animations = st.multiselect("Select animation types to generate:", animation_types)
        
        if st.button("Generate Selected Animations"):
            for anim_type in selected_animations:
                with st.spinner(f"Generating {anim_type} animation..."):
                    anim_url = generate_animation_variation(base_prompt, anim_type)
                    if anim_url:
                        st.session_state.animations[anim_type] = anim_url
                        st.image(anim_url, caption=f"{anim_type.capitalize()} Animation")
    
    # Spritesheet construction
    if st.session_state.animations:
        st.header("3. Build Spritesheet")
        st.write("Your generated animations will appear here for spritesheet construction.")
        # TODO: Implement spritesheet construction functionality

if __name__ == "__main__":
    main() 