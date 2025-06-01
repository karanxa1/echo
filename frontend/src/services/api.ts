import axios, { AxiosInstance } from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

class ApiService {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.instance.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearAuthToken();
          if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
          }
        } else if (error.response?.status >= 500) {
          toast.error('Server error. Please try again later.');
        }
        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token: string) {
    this.instance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  clearAuthToken() {
    delete this.instance.defaults.headers.common['Authorization'];
  }

  async get(url: string, config?: any) {
    return this.instance.get(url, config);
  }

  async post(url: string, data?: any, config?: any) {
    return this.instance.post(url, data, config);
  }

  async put(url: string, data?: any, config?: any) {
    return this.instance.put(url, data, config);
  }

  async delete(url: string, config?: any) {
    return this.instance.delete(url, config);
  }

  // Memory endpoints
  async createTextMemory(data: { content: string; title?: string; source?: string }) {
    return this.post('/memories/text', data);
  }

  async uploadVoiceMemory(file: File, title?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    
    return this.post('/memories/upload/voice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  async uploadImageMemory(file: File, title?: string, description?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);
    
    return this.post('/memories/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  async getMemories(params?: { skip?: number; limit?: number; content_type?: string; source?: string }) {
    return this.get('/memories/', { params });
  }

  async searchMemories(query: string, limit = 10) {
    return this.post('/memories/search', { query, limit });
  }

  async deleteMemory(id: number) {
    return this.delete(`/memories/${id}`);
  }

  // Replica endpoints
  async createReplica(data: any) {
    return this.post('/replicas/', data);
  }

  async getReplicas() {
    return this.get('/replicas/');
  }

  async getReplica(id: number) {
    return this.get(`/replicas/${id}`);
  }

  async updateReplica(id: number, data: any) {
    return this.put(`/replicas/${id}`, data);
  }

  async deleteReplica(id: number) {
    return this.delete(`/replicas/${id}`);
  }

  async trainReplica(id: number) {
    return this.post(`/replicas/${id}/train`);
  }

  // Chat endpoints
  async chatWithSelf(message: string, conversationId?: number) {
    return this.post('/chat/self', { message, conversation_id: conversationId });
  }

  async chatWithReplica(message: string, replicaId: number, conversationId?: number) {
    return this.post('/chat/replica', { 
      message, 
      replica_id: replicaId, 
      conversation_id: conversationId 
    });
  }

  async getConversations() {
    return this.get('/chat/conversations');
  }

  async getConversationMessages(conversationId: number) {
    return this.get(`/chat/conversations/${conversationId}/messages`);
  }

  async deleteConversation(conversationId: number) {
    return this.delete(`/chat/conversations/${conversationId}`);
  }

  async getChatSuggestions(type: 'self' | 'replica', replicaId?: number) {
    return this.get('/chat/suggestions', { 
      params: { conversation_type: type, replica_id: replicaId }
    });
  }

  // Advanced AI Services
  async getAIServices() {
    return this.get('/chat/ai-services');
  }

  async chatWithAIService(serviceId: string, message: string, conversationId?: number) {
    return this.post('/chat/ai-chat', {
      service_id: serviceId,
      message,
      conversation_id: conversationId
    });
  }

  async getAIServiceSuggestions(serviceId: string) {
    return this.get(`/chat/ai-suggestions/${serviceId}`);
  }

  async getSmartSuggestions(message: string, recentTopics: string[] = []) {
    return this.post('/chat/smart-suggestions', {
      message,
      recent_topics: recentTopics
    });
  }

  // Stats endpoints
  async getMemoryStats() {
    return this.get('/memories/stats/overview');
  }

  async getChatStats() {
    return this.get('/chat/stats');
  }

  async getReplicaStats(id: number) {
    return this.get(`/replicas/${id}/stats`);
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Store the token
    localStorage.setItem('access_token', data.access_token);
    
    return data;
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(errorData.detail || 'Registration failed');
    }

    return await response.json();
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to get user info');
    }

    return await response.json();
  }

  async verifyToken(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/verify`, {
        headers: this.getAuthHeaders(),
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  logout(): void {
    localStorage.removeItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  private getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }
}

export const apiService = new ApiService(); 