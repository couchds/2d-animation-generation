import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Update this with your backend URL

interface SpriteResponse {
  id: string;
  url: string;
  description: string;
}

export const generateSprite = async (prompt: string): Promise<SpriteResponse> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/sprites/generate`, {
      description: prompt,
    });
    return response.data;
  } catch (error) {
    console.error('Error generating sprite:', error);
    throw error;
  }
};

export const getAllSprites = async (): Promise<SpriteResponse[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/sprites`);
    return response.data;
  } catch (error) {
    console.error('Error fetching sprites:', error);
    throw error;
  }
}; 