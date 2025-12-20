/**
 * Tests for lib/api-client.ts
 */
import { apiClient, flightsApi, flightCrewApi, cabinCrewApi, passengersApi } from '@/lib/api-client';
import { authService } from '@/lib/auth';

// Mock the auth service
jest.mock('@/lib/auth', () => ({
    authService: {
        getAuthHeader: jest.fn(),
        logout: jest.fn(),
    },
}));

// Mock fetch globally
global.fetch = jest.fn();

// Mock window.location
const mockLocation = { href: '' };
Object.defineProperty(window, 'location', {
    value: mockLocation,
    writable: true,
});

describe('ApiClient', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        (authService.getAuthHeader as jest.Mock).mockReturnValue({
            Authorization: 'Bearer test-token',
        });
        mockLocation.href = '';
    });

    describe('GET requests', () => {
        it('should make GET request with authorization header', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ data: 'test' }),
            });

            const result = await apiClient.get('/test-endpoint');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/test-endpoint'),
                expect.objectContaining({
                    method: 'GET',
                    headers: expect.objectContaining({
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer test-token',
                    }),
                })
            );
            expect(result).toEqual({ data: 'test' });
        });

        it('should handle 401 error by logging out and redirecting', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 401,
                json: () => Promise.resolve({ detail: 'Unauthorized' }),
            });

            await expect(apiClient.get('/test-endpoint')).rejects.toThrow();
            expect(authService.logout).toHaveBeenCalled();
            expect(mockLocation.href).toBe('/login');
        });

        it('should handle non-401 errors', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 404,
                json: () => Promise.resolve({ detail: 'Not found' }),
            });

            await expect(apiClient.get('/test-endpoint')).rejects.toThrow('Not found');
        });

        it('should handle JSON parse errors', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 500,
                json: () => Promise.reject(new Error('Invalid JSON')),
            });

            await expect(apiClient.get('/test-endpoint')).rejects.toThrow('Request failed');
        });
    });

    describe('POST requests', () => {
        it('should make POST request with body', async () => {
            const postData = { name: 'Test' };
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ id: 1, name: 'Test' }),
            });

            const result = await apiClient.post('/test-endpoint', postData);

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/test-endpoint'),
                expect.objectContaining({
                    method: 'POST',
                    body: JSON.stringify(postData),
                })
            );
            expect(result).toEqual({ id: 1, name: 'Test' });
        });

        it('should make POST request without body', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ success: true }),
            });

            const result = await apiClient.post('/test-endpoint');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/test-endpoint'),
                expect.objectContaining({
                    method: 'POST',
                    body: undefined,
                })
            );
            expect(result).toEqual({ success: true });
        });
    });

    describe('PUT requests', () => {
        it('should make PUT request with body', async () => {
            const putData = { id: 1, name: 'Updated' };
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(putData),
            });

            const result = await apiClient.put('/test-endpoint/1', putData);

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/test-endpoint/1'),
                expect.objectContaining({
                    method: 'PUT',
                    body: JSON.stringify(putData),
                })
            );
            expect(result).toEqual(putData);
        });
    });

    describe('DELETE requests', () => {
        it('should make DELETE request', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ deleted: true }),
            });

            const result = await apiClient.delete('/test-endpoint/1');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/test-endpoint/1'),
                expect.objectContaining({
                    method: 'DELETE',
                })
            );
            expect(result).toEqual({ deleted: true });
        });
    });

    describe('flightsApi', () => {
        it('should get all flights', async () => {
            const flights = [{ id: 1, flight_number: 'TK001' }];
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(flights),
            });

            const result = await flightsApi.getAll();

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/flight-info/'),
                expect.any(Object)
            );
            expect(result).toEqual(flights);
        });

        it('should get flight by ID', async () => {
            const flight = { id: 1, flight_number: 'TK001' };
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(flight),
            });

            const result = await flightsApi.getById('1');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/flight-info/1'),
                expect.any(Object)
            );
            expect(result).toEqual(flight);
        });

        it('should create flight', async () => {
            const newFlight = { flight_number: 'TK002' };
            const createdFlight = { id: 2, ...newFlight };
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(createdFlight),
            });

            const result = await flightsApi.create(newFlight);

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/flight-info/'),
                expect.objectContaining({
                    method: 'POST',
                })
            );
            expect(result).toEqual(createdFlight);
        });

        it('should update flight', async () => {
            const updatedFlight = { id: 1, flight_number: 'TK001-UPDATED' };
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(updatedFlight),
            });

            const result = await flightsApi.update('1', updatedFlight);

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/flight-info/1'),
                expect.objectContaining({
                    method: 'PUT',
                })
            );
            expect(result).toEqual(updatedFlight);
        });

        it('should delete flight', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ deleted: true }),
            });

            const result = await flightsApi.delete('1');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/flight-info/1'),
                expect.objectContaining({
                    method: 'DELETE',
                })
            );
        });
    });

    describe('flightCrewApi', () => {
        it('should get all flight crew', async () => {
            const crew = [{ id: 1, name: 'Captain Smith' }];
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(crew),
            });

            const result = await flightCrewApi.getAll();

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/flight-crew/'),
                expect.any(Object)
            );
            expect(result).toEqual(crew);
        });

        it('should get flight crew by flight ID', async () => {
            const crew = [{ id: 1, name: 'Captain Smith' }];
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(crew),
            });

            const result = await flightCrewApi.getByFlight('1');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/flight-crew/flight/1'),
                expect.any(Object)
            );
            expect(result).toEqual(crew);
        });
    });

    describe('cabinCrewApi', () => {
        it('should get all cabin crew', async () => {
            const crew = [{ id: 1, name: 'Sarah Attendant' }];
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(crew),
            });

            const result = await cabinCrewApi.getAll();

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/cabin-crew/'),
                expect.any(Object)
            );
            expect(result).toEqual(crew);
        });

        it('should get cabin crew by flight ID', async () => {
            const crew = [{ id: 1, name: 'Sarah Attendant' }];
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(crew),
            });

            const result = await cabinCrewApi.getByFlight('1');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/cabin-crew/flight/1'),
                expect.any(Object)
            );
            expect(result).toEqual(crew);
        });
    });

    describe('passengersApi', () => {
        it('should get all passengers', async () => {
            const passengers = [{ id: 1, name: 'John Doe' }];
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(passengers),
            });

            const result = await passengersApi.getAll();

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/passenger/'),
                expect.any(Object)
            );
            expect(result).toEqual(passengers);
        });

        it('should get passengers by flight ID', async () => {
            const passengers = [{ id: 1, name: 'John Doe' }];
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(passengers),
            });

            const result = await passengersApi.getByFlight('1');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/passenger/flight/1'),
                expect.any(Object)
            );
            expect(result).toEqual(passengers);
        });

        it('should create passenger', async () => {
            const newPassenger = { name: 'Jane Doe', email: 'jane@example.com' };
            const createdPassenger = { id: 2, ...newPassenger };
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(createdPassenger),
            });

            const result = await passengersApi.create(newPassenger);

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/passenger/'),
                expect.objectContaining({
                    method: 'POST',
                })
            );
            expect(result).toEqual(createdPassenger);
        });

        it('should update passenger', async () => {
            const updatedPassenger = { id: 1, name: 'John Updated' };
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(updatedPassenger),
            });

            const result = await passengersApi.update('1', updatedPassenger);

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/passenger/1'),
                expect.objectContaining({
                    method: 'PUT',
                })
            );
            expect(result).toEqual(updatedPassenger);
        });

        it('should delete passenger', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ deleted: true }),
            });

            await passengersApi.delete('1');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/passenger/1'),
                expect.objectContaining({
                    method: 'DELETE',
                })
            );
        });
    });
});
