import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export interface SpriteResponse {
  id: string;
  url: string;
  description: string;
}

export const spriteService = {
  generateSprite: async (description: string): Promise<SpriteResponse> => {
    const response = await axios.post(`${API_BASE_URL}/sprites/generate`, {
      description,
    });
    return response.data;
  },

  getSprite: async (spriteId: string): Promise<SpriteResponse> => {
    const response = await axios.get(`${API_BASE_URL}/sprites/${spriteId}`);
    return response.data;
  },
}; 