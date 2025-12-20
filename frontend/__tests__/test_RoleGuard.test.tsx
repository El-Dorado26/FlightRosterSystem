/**
 * RoleGuard Tests
 * Tests for role-based access control components
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { RoleGuard, FeatureGuard } from '@/components/auth/role-guard';
import { useAuth } from '@/contexts/AuthContext';

// Mock useAuth hook
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

describe('RoleGuard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('RoleGuard component', () => {
    it('should render children when user has allowed role', () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
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
        hasRole: jest.fn(),
      });

      render(
        <RoleGuard allowedRoles={['admin', 'manager']}>
          <div data-testid="protected-content">Protected Content</div>
        </RoleGuard>
      );

      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('should hide content when user does not have allowed role', () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 2,
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
        hasRole: jest.fn(),
      });

      render(
        <RoleGuard allowedRoles={['admin', 'manager']}>
          <div data-testid="protected-content">Protected Content</div>
        </RoleGuard>
      );

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });

    it('should show fallback when user is not authorized', () => {
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
        hasRole: jest.fn(),
      });

      render(
        <RoleGuard
          allowedRoles={['admin']}
          fallback={<div data-testid="fallback">Access Denied</div>}
        >
          <div data-testid="protected-content">Protected Content</div>
        </RoleGuard>
      );

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
      expect(screen.getByTestId('fallback')).toBeInTheDocument();
      expect(screen.getByText('Access Denied')).toBeInTheDocument();
    });

    it('should show fallback when no user is logged in', () => {
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
        <RoleGuard
          allowedRoles={['admin', 'manager']}
          fallback={<div data-testid="fallback">Please Login</div>}
        >
          <div data-testid="protected-content">Protected Content</div>
        </RoleGuard>
      );

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
      expect(screen.getByTestId('fallback')).toBeInTheDocument();
      expect(screen.getByText('Please Login')).toBeInTheDocument();
    });

    it('should render nothing when no fallback is provided and user is unauthorized', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        loading: false,
        login: jest.fn(),
        register: jest.fn(),
        logout: jest.fn(),
        isAuthenticated: false,
        hasRole: jest.fn(),
      });

      const { container } = render(
        <RoleGuard allowedRoles={['admin']}>
          <div data-testid="protected-content">Protected Content</div>
        </RoleGuard>
      );

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
      expect(container.firstChild).toBeNull();
    });
  });

  describe('FeatureGuard component', () => {
    it('should grant admin full access to all features', () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
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
        hasRole: jest.fn(),
      });

      const features = ['view', 'export', 'save', 'edit', 'delete'] as const;

      features.forEach((feature) => {
        const { unmount } = render(
          <FeatureGuard feature={feature}>
            <div data-testid={`feature-${feature}`}>{feature} content</div>
          </FeatureGuard>
        );

        expect(screen.getByTestId(`feature-${feature}`)).toBeInTheDocument();
        unmount();
      });
    });

    it('should grant manager limited access (no delete)', () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 2,
          email: 'manager@example.com',
          full_name: 'Manager User',
          role: 'manager',
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

      // Manager should have access to these
      const allowedFeatures = ['view', 'export', 'save', 'edit'] as const;
      allowedFeatures.forEach((feature) => {
        const { unmount } = render(
          <FeatureGuard feature={feature}>
            <div data-testid={`feature-${feature}`}>{feature} content</div>
          </FeatureGuard>
        );

        expect(screen.getByTestId(`feature-${feature}`)).toBeInTheDocument();
        unmount();
      });

      // Manager should NOT have access to delete
      render(
        <FeatureGuard feature="delete">
          <div data-testid="feature-delete">delete content</div>
        </FeatureGuard>
      );
      expect(screen.queryByTestId('feature-delete')).not.toBeInTheDocument();
    });

    it('should grant viewer read-only access', () => {
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
        hasRole: jest.fn(),
      });

      // Viewer should only have view access
      const { unmount } = render(
        <FeatureGuard feature="view">
          <div data-testid="feature-view">view content</div>
        </FeatureGuard>
      );
      expect(screen.getByTestId('feature-view')).toBeInTheDocument();
      unmount();

      // Viewer should NOT have access to other features
      const deniedFeatures = ['export', 'save', 'edit', 'delete'] as const;
      deniedFeatures.forEach((feature) => {
        const { unmount } = render(
          <FeatureGuard feature={feature}>
            <div data-testid={`feature-${feature}`}>{feature} content</div>
          </FeatureGuard>
        );

        expect(screen.queryByTestId(`feature-${feature}`)).not.toBeInTheDocument();
        unmount();
      });
    });

    it('should validate user role correctly', () => {
      // Test with crew role
      mockUseAuth.mockReturnValue({
        user: {
          id: 4,
          email: 'crew@example.com',
          full_name: 'Crew User',
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

      // User/crew should have view access
      const { container } = render(
        <FeatureGuard feature="view">
          <div data-testid="feature-view">view content</div>
        </FeatureGuard>
      );

      // User role doesn't have view permission, so content should not be visible
      expect(screen.queryByTestId('feature-view')).not.toBeInTheDocument();
    });

    it('should deny all access when no user is logged in', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        loading: false,
        login: jest.fn(),
        register: jest.fn(),
        logout: jest.fn(),
        isAuthenticated: false,
        hasRole: jest.fn(),
      });

      const features = ['view', 'export', 'save', 'edit', 'delete'] as const;

      features.forEach((feature) => {
        const { unmount } = render(
          <FeatureGuard feature={feature}>
            <div data-testid={`feature-${feature}`}>{feature} content</div>
          </FeatureGuard>
        );

        expect(screen.queryByTestId(`feature-${feature}`)).not.toBeInTheDocument();
        unmount();
      });
    });
  });
});
