/**
 * Tests for lib/auth.ts
 */
import { authService, User, AuthResponse } from '@/lib/auth';

// Mock fetch globally
global.fetch = jest.fn();

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
        clear: jest.fn(() => {
            store = {};
        }),
        get length() {
            return Object.keys(store).length;
        },
        key: jest.fn((i: number) => Object.keys(store)[i] || null),
    };
})();

Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    writable: true,
});

describe('AuthService', () => {
    const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'admin',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
    };

    const mockAuthResponse: AuthResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        user: mockUser,
    };

    beforeEach(() => {
        jest.clearAllMocks();
        localStorageMock.clear();
    });

    describe('login', () => {
        it('should login successfully and store token', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockAuthResponse),
            });

            const result = await authService.login({
                email: 'test@example.com',
                password: 'password123',
            });

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/auth/login'),
                expect.objectContaining({
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: 'test@example.com',
                        password: 'password123',
                    }),
                })
            );

            expect(localStorageMock.setItem).toHaveBeenCalledWith(
                'auth_token',
                'test-token'
            );
            expect(localStorageMock.setItem).toHaveBeenCalledWith(
                'auth_user',
                JSON.stringify(mockUser)
            );
            expect(result).toEqual(mockAuthResponse);
        });

        it('should throw error on login failure', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                json: () => Promise.resolve({ detail: 'Invalid credentials' }),
            });

            await expect(
                authService.login({
                    email: 'test@example.com',
                    password: 'wrong-password',
                })
            ).rejects.toThrow('Invalid credentials');
        });

        it('should throw generic error when no detail provided', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                json: () => Promise.resolve({}),
            });

            await expect(
                authService.login({
                    email: 'test@example.com',
                    password: 'password',
                })
            ).rejects.toThrow('Login failed');
        });
    });

    describe('register', () => {
        it('should register successfully and store token', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockAuthResponse),
            });

            const result = await authService.register({
                email: 'new@example.com',
                password: 'password123',
                full_name: 'New User',
                role: 'user',
            });

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/auth/register'),
                expect.objectContaining({
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: 'new@example.com',
                        password: 'password123',
                        full_name: 'New User',
                        role: 'user',
                    }),
                })
            );

            expect(localStorageMock.setItem).toHaveBeenCalledWith(
                'auth_token',
                'test-token'
            );
            expect(result).toEqual(mockAuthResponse);
        });

        it('should throw error on registration failure', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                json: () => Promise.resolve({ detail: 'Email already exists' }),
            });

            await expect(
                authService.register({
                    email: 'existing@example.com',
                    password: 'password123',
                    full_name: 'Test User',
                })
            ).rejects.toThrow('Email already exists');
        });
    });

    describe('logout', () => {
        it('should clear token and user from localStorage', () => {
            localStorageMock.setItem('auth_token', 'test-token');
            localStorageMock.setItem('auth_user', JSON.stringify(mockUser));

            authService.logout();

            expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
            expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user');
        });
    });

    describe('getCurrentUser', () => {
        it('should fetch current user from API', async () => {
            localStorageMock.setItem('auth_token', 'test-token');
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce('test-token');

            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockUser),
            });

            const result = await authService.getCurrentUser();

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/auth/me'),
                expect.objectContaining({
                    headers: { Authorization: 'Bearer test-token' },
                })
            );
            expect(result).toEqual(mockUser);
        });

        it('should throw error when no token exists', async () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce(null);

            await expect(authService.getCurrentUser()).rejects.toThrow(
                'No authentication token found'
            );
        });

        it('should logout on 401 error', async () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce('test-token');

            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 401,
            });

            await expect(authService.getCurrentUser()).rejects.toThrow(
                'Failed to get user info'
            );
            expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
        });
    });

    describe('refreshToken', () => {
        it('should refresh token successfully', async () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce('old-token');

            const newAuthResponse = {
                ...mockAuthResponse,
                access_token: 'new-token',
            };

            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(newAuthResponse),
            });

            const result = await authService.refreshToken();

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/auth/refresh'),
                expect.objectContaining({
                    method: 'POST',
                    headers: { Authorization: 'Bearer old-token' },
                })
            );
            expect(localStorageMock.setItem).toHaveBeenCalledWith(
                'auth_token',
                'new-token'
            );
            expect(result).toEqual(newAuthResponse);
        });

        it('should throw error when no token exists', async () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce(null);

            await expect(authService.refreshToken()).rejects.toThrow(
                'No authentication token found'
            );
        });

        it('should logout on refresh failure', async () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce('old-token');

            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 401,
            });

            await expect(authService.refreshToken()).rejects.toThrow(
                'Token refresh failed'
            );
            expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
        });
    });

    describe('isAuthenticated', () => {
        it('should return true when token exists', () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce('test-token');

            expect(authService.isAuthenticated()).toBe(true);
        });

        it('should return false when no token exists', () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce(null);

            expect(authService.isAuthenticated()).toBe(false);
        });
    });

    describe('getToken', () => {
        it('should return token from localStorage', () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce('test-token');

            expect(authService.getToken()).toBe('test-token');
        });

        it('should return null when no token exists', () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce(null);

            expect(authService.getToken()).toBeNull();
        });
    });

    describe('getUser', () => {
        it('should return user from localStorage', () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce(
                JSON.stringify(mockUser)
            );

            expect(authService.getUser()).toEqual(mockUser);
        });

        it('should return null when no user exists', () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce(null);

            expect(authService.getUser()).toBeNull();
        });
    });

    describe('getAuthHeader', () => {
        it('should return authorization header when token exists', () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce('test-token');

            expect(authService.getAuthHeader()).toEqual({
                Authorization: 'Bearer test-token',
            });
        });

        it('should return empty object when no token exists', () => {
            (localStorageMock.getItem as jest.Mock).mockReturnValueOnce(null);

            expect(authService.getAuthHeader()).toEqual({});
        });
    });
});
