import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export interface AnimationResponse {
  id: string;
  url: string;
  animation_type: string;
  base_sprite_id: string;
}

export const animationService = {
  generateAnimation: async (
    baseSpriteId: string,
    animationType: string
  ): Promise<AnimationResponse> => {
    const response = await axios.post(`${API_BASE_URL}/animations/generate`, {
      base_sprite_id: baseSpriteId,
      animation_type: animationType,
    });
    return response.data;
  },

  getAnimation: async (animationId: string): Promise<AnimationResponse> => {
    const response = await axios.get(`${API_BASE_URL}/animations/${animationId}`);
    return response.data;
  },

  getSpriteAnimations: async (
    spriteId: string
  ): Promise<AnimationResponse[]> => {
    const response = await axios.get(
      `${API_BASE_URL}/animations/sprite/${spriteId}`
    );
    return response.data;
  },
}; 