import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Update this with your backend URL

interface SpriteResponse {
  id: string;
  url: string;
  description: string;
  parent_id?: string;
  edit_description?: string;
  created_at?: string;
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

interface EditImageRequest {
  spriteId: string;
  prompt: string;
  num_variations?: number;
}

export const editSpriteImage = async (params: EditImageRequest): Promise<SpriteResponse[]> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/sprites/edit`, params);
    return response.data;
  } catch (error) {
    console.error('Error editing sprite:', error);
    throw error;
  }
};

interface SpriteHistoryResponse {
  current: SpriteResponse;
  ancestors: SpriteResponse[];
  children: SpriteResponse[];
  timeline: SpriteResponse[];
}

export const getSpriteHistory = async (spriteId: string): Promise<SpriteHistoryResponse> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/sprites/history/${spriteId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching sprite history:', error);
    throw error;
  }
}; 