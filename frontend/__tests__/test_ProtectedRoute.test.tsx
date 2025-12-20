/**
 * ProtectedRoute Tests
 * Tests for protected route authentication component
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;
const mockPush = jest.fn();

describe('ProtectedRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseRouter.mockReturnValue({
      push: mockPush,
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    } as any);
  });

  it('should show loading state while checking authentication', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: true,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
      isAuthenticated: false,
      hasRole: jest.fn(),
    });

    render(
      <ProtectedRoute>
        <div data-testid="protected-content">Protected Content</div>
      </ProtectedRoute>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  it('should render children when user is authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'admin',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      },
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
      isAuthenticated: true,
      hasRole: jest.fn(),
    });

    render(
      <ProtectedRoute>
        <div data-testid="protected-content">Protected Content</div>
      </ProtectedRoute>
    );

    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should redirect to login when user is not authenticated', async () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
      isAuthenticated: false,
      hasRole: jest.fn(),
    });

    render(
      <ProtectedRoute>
        <div data-testid="protected-content">Protected Content</div>
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login');
    });

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  it('should allow access when user has required role', () => {
    const mockHasRole = jest.fn().mockReturnValue(true);

    mockUseAuth.mockReturnValue({
      user: {
        id: 2,
        email: 'admin@example.com',
        full_name: 'Admin User',
        role: 'admin',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      },
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
      isAuthenticated: true,
      hasRole: mockHasRole,
    });

    render(
      <ProtectedRoute allowedRoles={['admin']}>
        <div data-testid="protected-content">Admin Content</div>
      </ProtectedRoute>
    );

    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    expect(mockHasRole).toHaveBeenCalledWith(['admin']);
  });

  it('should redirect to unauthorized when user lacks required role', async () => {
    const mockHasRole = jest.fn().mockReturnValue(false);

    mockUseAuth.mockReturnValue({
      user: {
        id: 3,
        email: 'viewer@example.com',
        full_name: 'Viewer User',
        role: 'viewer',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      },
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
      isAuthenticated: true,
      hasRole: mockHasRole,
    });

    render(
      <ProtectedRoute allowedRoles={['admin', 'manager']}>
        <div data-testid="protected-content">Admin Content</div>
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/unauthorized');
    });

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    expect(mockHasRole).toHaveBeenCalledWith(['admin', 'manager']);
  });

  it('should work without role restrictions', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 4,
        email: 'user@example.com',
        full_name: 'Regular User',
        role: 'user',
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
      },
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
      isAuthenticated: true,
      hasRole: jest.fn(),
    });

    render(
      <ProtectedRoute>
        <div data-testid="protected-content">General Content</div>
      </ProtectedRoute>
    );

    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    expect(mockPush).not.toHaveBeenCalled();
  });
});
