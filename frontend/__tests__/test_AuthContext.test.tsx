import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { authService, User, AuthResponse } from '@/lib/auth';

jest.mock('@/lib/auth', () => ({
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    getUser: jest.fn(),
    getCurrentUser: jest.fn(),
    isAuthenticated: jest.fn(),
  },
}));

function TestComponent() {
  const { user, loading, login, register, logout, isAuthenticated, hasRole } = useAuth();
  
  return (
    <div>
      <div data-testid="loading">{loading ? 'loading' : 'loaded'}</div>
      <div data-testid="authenticated">{isAuthenticated ? 'yes' : 'no'}</div>
      <div data-testid="user-email">{user?.email || 'none'}</div>
      <div data-testid="user-role">{user?.role || 'none'}</div>
      <button onClick={() => login('test@example.com', 'password')}>Login</button>
      <button onClick={() => register('new@example.com', 'password', 'New User', 'viewer')}>
        Register
      </button>
      <button onClick={logout}>Logout</button>
      <div data-testid="has-admin-role">{hasRole(['admin']) ? 'yes' : 'no'}</div>
      <div data-testid="has-manager-role">{hasRole(['manager']) ? 'yes' : 'no'}</div>
      <div data-testid="has-viewer-role">{hasRole(['viewer']) ? 'yes' : 'no'}</div>
    </div>
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('AuthProvider component', () => {
    it('should load user from localStorage on initial load', async () => {
      const mockUser: User = {
        id: 1,
        email: 'cached@example.com',
        full_name: 'Cached User',
        role: 'manager',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      };

      (authService.getUser as jest.Mock).mockReturnValue(mockUser);
      (authService.isAuthenticated as jest.Mock).mockReturnValue(true);
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      }, { timeout: 3000 });

      expect(screen.getByTestId('user-email')).toHaveTextContent('cached@example.com');
      expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
      expect(authService.getUser).toHaveBeenCalled();
    });

    it('should update state on successful login', async () => {
      const mockUser: User = {
        id: 2,
        email: 'login@example.com',
        full_name: 'Login User',
        role: 'admin',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      };

      const mockResponse: AuthResponse = {
        access_token: 'mock-token',
        token_type: 'bearer',
        user: mockUser,
      };

      (authService.getUser as jest.Mock).mockReturnValue(null);
      (authService.isAuthenticated as jest.Mock).mockReturnValue(false);
      (authService.login as jest.Mock).mockResolvedValue(mockResponse);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      });

      // Initial state - no user
      expect(screen.getByTestId('user-email')).toHaveTextContent('none');
      expect(screen.getByTestId('authenticated')).toHaveTextContent('no');

      // Trigger login
      await act(async () => {
        screen.getByText('Login').click();
      });

      await waitFor(() => {
        expect(screen.getByTestId('user-email')).toHaveTextContent('login@example.com');
      });

      expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
      expect(screen.getByTestId('user-role')).toHaveTextContent('admin');
      expect(authService.login).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password' });
    });

    it('should clear state on logout', async () => {
      const mockUser: User = {
        id: 3,
        email: 'logout@example.com',
        full_name: 'Logout User',
        role: 'viewer',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      };

      (authService.getUser as jest.Mock).mockReturnValue(mockUser);
      (authService.isAuthenticated as jest.Mock).mockReturnValue(true);
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user-email')).toHaveTextContent('logout@example.com');
      });

      // Trigger logout
      act(() => {
        screen.getByText('Logout').click();
      });

      expect(screen.getByTestId('user-email')).toHaveTextContent('none');
      expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
      expect(authService.logout).toHaveBeenCalled();
    });

    it('should create user on successful registration', async () => {
      const mockUser: User = {
        id: 4,
        email: 'new@example.com',
        full_name: 'New User',
        role: 'viewer',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      };

      const mockResponse: AuthResponse = {
        access_token: 'mock-token',
        token_type: 'bearer',
        user: mockUser,
      };

      (authService.getUser as jest.Mock).mockReturnValue(null);
      (authService.isAuthenticated as jest.Mock).mockReturnValue(false);
      (authService.register as jest.Mock).mockResolvedValue(mockResponse);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      });

      // Trigger registration
      await act(async () => {
        screen.getByText('Register').click();
      });

      await waitFor(() => {
        expect(screen.getByTestId('user-email')).toHaveTextContent('new@example.com');
      });

      expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
      expect(authService.register).toHaveBeenCalledWith({
        email: 'new@example.com',
        password: 'password',
        full_name: 'New User',
        role: 'viewer',
      });
    });
  });

  describe('hasRole() utility', () => {
    it('should return true for matching role', async () => {
      const mockUser: User = {
        id: 5,
        email: 'admin@example.com',
        full_name: 'Admin User',
        role: 'admin',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      };

      (authService.getUser as jest.Mock).mockReturnValue(mockUser);
      (authService.isAuthenticated as jest.Mock).mockReturnValue(true);
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user-email')).toHaveTextContent('admin@example.com');
      });

      expect(screen.getByTestId('has-admin-role')).toHaveTextContent('yes');
      expect(screen.getByTestId('has-manager-role')).toHaveTextContent('no');
    });

    it('should return false for non-matching role', async () => {
      const mockUser: User = {
        id: 6,
        email: 'viewer@example.com',
        full_name: 'Viewer User',
        role: 'viewer',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      };

      (authService.getUser as jest.Mock).mockReturnValue(mockUser);
      (authService.isAuthenticated as jest.Mock).mockReturnValue(true);
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user-email')).toHaveTextContent('viewer@example.com');
      });

      expect(screen.getByTestId('has-viewer-role')).toHaveTextContent('yes');
      expect(screen.getByTestId('has-admin-role')).toHaveTextContent('no');
      expect(screen.getByTestId('has-manager-role')).toHaveTextContent('no');
    });

    it('should return false when no user is logged in', async () => {
      (authService.getUser as jest.Mock).mockReturnValue(null);
      (authService.isAuthenticated as jest.Mock).mockReturnValue(false);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      });

      expect(screen.getByTestId('has-admin-role')).toHaveTextContent('no');
      expect(screen.getByTestId('has-manager-role')).toHaveTextContent('no');
      expect(screen.getByTestId('has-viewer-role')).toHaveTextContent('no');
    });
  });
});
