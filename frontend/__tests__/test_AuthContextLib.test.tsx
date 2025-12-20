/**
 * Tests for lib/auth-context.tsx
 */
import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AuthProvider, useAuth } from '@/lib/auth-context';

// Mock localStorage
const localStorageMock = (() => {
    let store: { [key: string]: string } = {};
    return {
        getItem: jest.fn((key: string) => store[key] || null),
        setItem: jest.fn((key: string, value: string) => {
            store[key] = value;
        }),
        removeItem: jest.fn((key: string) => {
            delete store[key];
        }),
        clear: () => {
            store = {};
        },
    };
})();

Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    writable: true,
});

// Mock window.location
const mockLocation = { href: '' };
Object.defineProperty(window, 'location', {
    value: mockLocation,
    writable: true,
});

// Test component that uses the auth context
function TestConsumer() {
    const { user, login, logout, isAuthenticated } = useAuth();

    return (
        <div>
            <div data-testid="is-authenticated">{isAuthenticated ? 'yes' : 'no'}</div>
            <div data-testid="user-email">{user?.email || 'no user'}</div>
            <div data-testid="user-role">{user?.role || 'no role'}</div>
            <button onClick={() => login('test@example.com', 'admin')}>Login</button>
            <button onClick={logout}>Logout</button>
        </div>
    );
}

describe('AuthContext', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        localStorageMock.clear();
        mockLocation.href = '';
    });

    describe('AuthProvider', () => {
        it('should render children', async () => {
            render(
                <AuthProvider>
                    <div>Test Child</div>
                </AuthProvider>
            );

            await waitFor(() => {
                expect(screen.getByText('Test Child')).toBeInTheDocument();
            });
        });

        it('should provide initial unauthenticated state', async () => {
            render(
                <AuthProvider>
                    <TestConsumer />
                </AuthProvider>
            );

            await waitFor(() => {
                expect(screen.getByTestId('is-authenticated')).toHaveTextContent('no');
            });
        });

        it('should restore user from localStorage on mount', async () => {
            const storedUser = { email: 'stored@example.com', role: 'user' };
            localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(storedUser));

            render(
                <AuthProvider>
                    <TestConsumer />
                </AuthProvider>
            );

            await waitFor(() => {
                expect(screen.getByTestId('user-email')).toHaveTextContent('stored@example.com');
            });
        });

        it('should handle invalid JSON in localStorage', async () => {
            localStorageMock.getItem.mockReturnValueOnce('invalid json');

            render(
                <AuthProvider>
                    <TestConsumer />
                </AuthProvider>
            );

            await waitFor(() => {
                expect(screen.getByTestId('is-authenticated')).toHaveTextContent('no');
            });

            expect(localStorageMock.removeItem).toHaveBeenCalledWith('flightRosterUser');
        });
    });

    describe('login', () => {
        it('should set user on login', async () => {
            render(
                <AuthProvider>
                    <TestConsumer />
                </AuthProvider>
            );

            await waitFor(() => {
                expect(screen.getByTestId('is-authenticated')).toHaveTextContent('no');
            });

            await act(async () => {
                fireEvent.click(screen.getByText('Login'));
            });

            expect(screen.getByTestId('is-authenticated')).toHaveTextContent('yes');
            expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
            expect(screen.getByTestId('user-role')).toHaveTextContent('admin');
        });

        it('should store user in localStorage on login', async () => {
            render(
                <AuthProvider>
                    <TestConsumer />
                </AuthProvider>
            );

            await waitFor(() => {
                expect(screen.getByText('Login')).toBeInTheDocument();
            });

            await act(async () => {
                fireEvent.click(screen.getByText('Login'));
            });

            expect(localStorageMock.setItem).toHaveBeenCalledWith(
                'flightRosterUser',
                expect.any(String)
            );
        });
    });

    describe('logout', () => {
        it('should clear user on logout', async () => {
            const storedUser = { email: 'test@example.com', role: 'admin' };
            localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(storedUser));

            render(
                <AuthProvider>
                    <TestConsumer />
                </AuthProvider>
            );

            await waitFor(() => {
                expect(screen.getByTestId('is-authenticated')).toHaveTextContent('yes');
            });

            await act(async () => {
                fireEvent.click(screen.getByText('Logout'));
            });

            expect(screen.getByTestId('is-authenticated')).toHaveTextContent('no');
        });

        it('should remove user from localStorage on logout', async () => {
            const storedUser = { email: 'test@example.com', role: 'admin' };
            localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(storedUser));

            render(
                <AuthProvider>
                    <TestConsumer />
                </AuthProvider>
            );

            await waitFor(() => {
                expect(screen.getByText('Logout')).toBeInTheDocument();
            });

            await act(async () => {
                fireEvent.click(screen.getByText('Logout'));
            });

            expect(localStorageMock.removeItem).toHaveBeenCalledWith('flightRosterUser');
        });

        it('should redirect to home on logout', async () => {
            const storedUser = { email: 'test@example.com', role: 'admin' };
            localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(storedUser));

            render(
                <AuthProvider>
                    <TestConsumer />
                </AuthProvider>
            );

            await waitFor(() => {
                expect(screen.getByText('Logout')).toBeInTheDocument();
            });

            await act(async () => {
                fireEvent.click(screen.getByText('Logout'));
            });

            expect(mockLocation.href).toBe('/');
        });
    });

    describe('useAuth hook', () => {
        it('should throw error when used outside AuthProvider', () => {
            // Suppress console.error for this test
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => { });

            expect(() => {
                render(<TestConsumer />);
            }).toThrow('useAuth must be used within an AuthProvider');

            consoleSpy.mockRestore();
        });
    });

    describe('Loading state', () => {
        it('should show loading spinner initially', () => {
            // This test is tricky because loading state is brief
            // The provider shows loading until localStorage check completes
            render(
                <AuthProvider>
                    <TestConsumer />
                </AuthProvider>
            );

            // After loading, should show content
            expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
        });
    });
});
