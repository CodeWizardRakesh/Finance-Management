import axios from 'axios';
import { ApiRequest, ApiResponse } from '../types';

const API_BASE_URL = 'http://localhost:5000';

export const sendQuery = async (query: string): Promise<ApiResponse> => {
  try {
    const response = await axios.post<ApiResponse>(`${API_BASE_URL}/query`, {
      query
    } as ApiRequest, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error('Failed to send query to advisor. Make sure your Flask server is running on localhost:5000');
  }
};