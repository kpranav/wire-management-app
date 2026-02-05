/**
 * API service for making HTTP requests
 */
import axios, { AxiosInstance } from 'axios';
import type {
  Wire,
  WireCreate,
  WireUpdate,
  WireListResponse,
  LoginCredentials,
  RegisterData,
  AuthTokens,
  User,
} from '@/types/wire';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle token expiration
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(data: RegisterData): Promise<User> {
    const response = await this.client.post<User>('/api/auth/register', data);
    return response.data;
  }

  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await this.client.post<AuthTokens>('/api/auth/login', credentials);
    const { access_token, refresh_token } = response.data;

    // Store tokens
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/api/auth/me');
    return response.data;
  }

  // Wire endpoints
  async getWires(page = 1, pageSize = 20, status?: string): Promise<WireListResponse> {
    const params: Record<string, string | number> = { page, page_size: pageSize };
    if (status) {
      params.status = status;
    }
    const response = await this.client.get<WireListResponse>('/api/wires', { params });
    return response.data;
  }

  async getWire(id: number): Promise<Wire> {
    const response = await this.client.get<Wire>(`/api/wires/${id}`);
    return response.data;
  }

  async createWire(data: WireCreate): Promise<Wire> {
    const response = await this.client.post<Wire>('/api/wires', data);
    return response.data;
  }

  async updateWire(id: number, data: WireUpdate): Promise<Wire> {
    const response = await this.client.put<Wire>(`/api/wires/${id}`, data);
    return response.data;
  }

  async deleteWire(id: number): Promise<void> {
    await this.client.delete(`/api/wires/${id}`);
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

export const api = new ApiService();
