import { authService } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers = {
      'Content-Type': 'application/json',
      ...authService.getAuthHeader(),
      ...options.headers,
    };

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        authService.logout();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }

      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();

export const flightsApi = {
  getAll: () => apiClient.get('/flight-info/'),
  getById: (id: string) => apiClient.get(`/flight-info/${id}`),
  create: (data: any) => apiClient.post('/flight-info/', data),
  update: (id: string, data: any) => apiClient.put(`/flight-info/${id}`, data),
  delete: (id: string) => apiClient.delete(`/flight-info/${id}`),
};

export const flightCrewApi = {
  getAll: () => apiClient.get('/flight-crew/'),
  getById: (id: string) => apiClient.get(`/flight-crew/${id}`),
  getByFlight: (flightId: string) => apiClient.get(`/flight-crew/flight/${flightId}`),
  create: (data: any) => apiClient.post('/flight-crew/', data),
  update: (id: string, data: any) => apiClient.put(`/flight-crew/${id}`, data),
  delete: (id: string) => apiClient.delete(`/flight-crew/${id}`),
};

export const cabinCrewApi = {
  getAll: () => apiClient.get('/cabin-crew/'),
  getById: (id: string) => apiClient.get(`/cabin-crew/${id}`),
  getByFlight: (flightId: string) => apiClient.get(`/cabin-crew/flight/${flightId}`),
  create: (data: any) => apiClient.post('/cabin-crew/', data),
  update: (id: string, data: any) => apiClient.put(`/cabin-crew/${id}`, data),
  delete: (id: string) => apiClient.delete(`/cabin-crew/${id}`),
};

export const passengersApi = {
  getAll: () => apiClient.get('/passenger/'),
  getById: (id: string) => apiClient.get(`/passenger/${id}`),
  getByFlight: (flightId: string) => apiClient.get(`/passenger/flight/${flightId}`),
  create: (data: any) => apiClient.post('/passenger/', data),
  update: (id: string, data: any) => apiClient.put(`/passenger/${id}`, data),
  delete: (id: string) => apiClient.delete(`/passenger/${id}`),
};
