import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DashboardHeader } from '@/components/auth/dashboard-header';
import { useAuth } from '@/contexts/AuthContext';

jest.mock('@/contexts/AuthContext');

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

describe('DashboardHeader', () => {
    const mockLogout = jest.fn();

    const mockUser = {
        id: 1,
        email: 'admin@example.com',
        full_name: 'Admin User',
        role: 'admin' as const,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
    };

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('When user is logged in', () => {
        beforeEach(() => {
            mockUseAuth.mockReturnValue({
                user: mockUser,
                loading: false,
                login: jest.fn(),
                register: jest.fn(),
                logout: mockLogout,
                isAuthenticated: true,
                hasRole: jest.fn(),
            });
        });

        it('should render header with branding', () => {
            render(<DashboardHeader />);

            expect(screen.getByText('OpenAIrlines')).toBeInTheDocument();
            expect(screen.getByText('Flight Roster Management System')).toBeInTheDocument();
        });

        it('should display user email', () => {
            render(<DashboardHeader />);

            expect(screen.getByText('admin@example.com')).toBeInTheDocument();
        });

        it('should display user role badge', () => {
            render(<DashboardHeader />);

            expect(screen.getByText('admin')).toBeInTheDocument();
        });

        it('should have logout button', () => {
            render(<DashboardHeader />);

            expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
        });

        it('should call logout when logout button clicked', () => {
            render(<DashboardHeader />);

            const logoutButton = screen.getByRole('button', { name: /logout/i });
            fireEvent.click(logoutButton);

            expect(mockLogout).toHaveBeenCalled();
        });

        it('should display correct role icon for admin', () => {
            render(<DashboardHeader />);

            // Admin should have Shield icon
            const badge = screen.getByText('admin').closest('div');
            expect(badge).toContainElement(badge?.querySelector('svg') || null);
        });
    });

    describe('When user has different roles', () => {
        it('should display correct badge for manager role', () => {
            mockUseAuth.mockReturnValue({
                user: { ...mockUser, role: 'manager' },
                loading: false,
                login: jest.fn(),
                register: jest.fn(),
                logout: mockLogout,
                isAuthenticated: true,
                hasRole: jest.fn(),
            });

            render(<DashboardHeader />);

            expect(screen.getByText('manager')).toBeInTheDocument();
        });

        it('should display correct badge for user role', () => {
            mockUseAuth.mockReturnValue({
                user: { ...mockUser, role: 'user' },
                loading: false,
                login: jest.fn(),
                register: jest.fn(),
                logout: mockLogout,
                isAuthenticated: true,
                hasRole: jest.fn(),
            });

            render(<DashboardHeader />);

            expect(screen.getByText('user')).toBeInTheDocument();
        });

        it('should display correct badge for viewer role', () => {
            mockUseAuth.mockReturnValue({
                user: { ...mockUser, role: 'viewer' },
                loading: false,
                login: jest.fn(),
                register: jest.fn(),
                logout: mockLogout,
                isAuthenticated: true,
                hasRole: jest.fn(),
            });

            render(<DashboardHeader />);

            expect(screen.getByText('viewer')).toBeInTheDocument();
        });
    });

    describe('When user is not logged in', () => {
        it('should not display user info when user is null', () => {
            mockUseAuth.mockReturnValue({
                user: null,
                loading: false,
                login: jest.fn(),
                register: jest.fn(),
                logout: mockLogout,
                isAuthenticated: false,
                hasRole: jest.fn(),
            });

            render(<DashboardHeader />);

            expect(screen.queryByRole('button', { name: /logout/i })).not.toBeInTheDocument();
        });

        it('should still display branding elements', () => {
            mockUseAuth.mockReturnValue({
                user: null,
                loading: false,
                login: jest.fn(),
                register: jest.fn(),
                logout: mockLogout,
                isAuthenticated: false,
                hasRole: jest.fn(),
            });

            render(<DashboardHeader />);

            expect(screen.getByText('OpenAIrlines')).toBeInTheDocument();
        });
    });
});
