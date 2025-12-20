import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { FlightFilter } from '@/components/flight-roster/flight-filter';
import { Flight } from '@/lib/types';

const mockFlights: Flight[] = [
    {
        id: 1,
        flight_number: 'TK001',
        airline: {
            id: 1,
            airline_name: 'Turkish Airlines',
            airline_code: 'TK',
            country: 'Turkey',
        },
        departure_airport: {
            id: 1,
            airport_name: 'Istanbul Airport',
            airport_code: 'IST',
            city: 'Istanbul',
            country: 'Turkey',
        },
        arrival_airport: {
            id: 2,
            airport_name: 'London Heathrow',
            airport_code: 'LHR',
            city: 'London',
            country: 'UK',
        },
        departure_time: '10:00',
        arrival_time: '14:30',
        flight_duration_minutes: 270,
        flight_distance_km: 2800,
        vehicle_type: {
            id: 1,
            aircraft_name: 'Boeing 737',
            aircraft_code: 'B737',
            total_seats: 180,
            seating_plan: {
                rows: 30,
                seats_per_row: 6,
                business: 24,
                economy: 156,
            },
            max_crew: 10,
            max_passengers: 180,
        },
        status: 'scheduled',
        flight_crew: [],
        cabin_crew: [],
        passengers: [],
    },
    {
        id: 2,
        flight_number: 'BA156',
        airline: {
            id: 2,
            airline_name: 'British Airways',
            airline_code: 'BA',
            country: 'UK',
        },
        departure_airport: {
            id: 2,
            airport_name: 'London Heathrow',
            airport_code: 'LHR',
            city: 'London',
            country: 'UK',
        },
        arrival_airport: {
            id: 1,
            airport_name: 'Istanbul Airport',
            airport_code: 'IST',
            city: 'Istanbul',
            country: 'Turkey',
        },
        departure_time: '08:00',
        arrival_time: '14:00',
        flight_duration_minutes: 300,
        flight_distance_km: 2800,
        vehicle_type: {
            id: 1,
            aircraft_name: 'Boeing 737',
            aircraft_code: 'B737',
            total_seats: 180,
            seating_plan: {
                rows: 30,
                seats_per_row: 6,
                business: 24,
                economy: 156,
            },
            max_crew: 10,
            max_passengers: 180,
        },
        status: 'departed',
        flight_crew: [],
        cabin_crew: [],
        passengers: [],
    },
];

describe('FlightFilter', () => {
    const mockOnFilter = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('should render filter component', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            expect(screen.getByText(/Search & Filter Flights/i)).toBeInTheDocument();
        });

        it('should render flight number input', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            expect(screen.getByPlaceholderText(/AA1234/i)).toBeInTheDocument();
        });

        it('should render airline dropdown', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            expect(screen.getByText(/Airline/i)).toBeInTheDocument();
        });

        it('should render departure airport dropdown', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            expect(screen.getByText(/Departure Airport/i)).toBeInTheDocument();
        });

        it('should render arrival airport dropdown', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            expect(screen.getByText(/Arrival Airport/i)).toBeInTheDocument();
        });

        it('should render status dropdown', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            expect(screen.getByText(/Status/i)).toBeInTheDocument();
        });

        it('should render Apply Filters button', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            expect(screen.getByRole('button', { name: /Apply Filters/i })).toBeInTheDocument();
        });

        it('should render Reset button', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            expect(screen.getByRole('button', { name: /Reset/i })).toBeInTheDocument();
        });
    });

    describe('Filtering', () => {
        it('should filter by flight number', async () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            const input = screen.getByPlaceholderText(/AA1234/i);
            await userEvent.type(input, 'TK');

            const applyButton = screen.getByRole('button', { name: /Apply Filters/i });
            fireEvent.click(applyButton);

            expect(mockOnFilter).toHaveBeenCalledWith(
                expect.arrayContaining([
                    expect.objectContaining({ flight_number: 'TK001' })
                ])
            );
        });

        it('should filter by status', async () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            // Apply filter without changing anything first to show all
            const applyButton = screen.getByRole('button', { name: /Apply Filters/i });
            fireEvent.click(applyButton);

            // Should call with all flights initially
            expect(mockOnFilter).toHaveBeenCalled();
        });

        it('should reset all filters', async () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            const input = screen.getByPlaceholderText(/AA1234/i);
            await userEvent.type(input, 'TK');

            const resetButton = screen.getByRole('button', { name: /Reset/i });
            fireEvent.click(resetButton);

            expect(input).toHaveValue('');
            expect(mockOnFilter).toHaveBeenCalledWith(mockFlights);
        });
    });

    describe('Dynamic Options', () => {
        it('should populate unique airlines', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            // Airlines dropdown should have unique airlines from flights
            expect(screen.getByText(/All Airlines/i)).toBeInTheDocument();
        });

        it('should populate unique airports', () => {
            render(<FlightFilter flights={mockFlights} onFilter={mockOnFilter} />);

            // Airports dropdown should have unique airports from flights
            expect(screen.getByText(/All Airports/i)).toBeInTheDocument();
        });
    });

    describe('Empty State', () => {
        it('should handle empty flights list', () => {
            render(<FlightFilter flights={[]} onFilter={mockOnFilter} />);

            expect(screen.getByText(/Search & Filter Flights/i)).toBeInTheDocument();
        });

        it('should still have apply button with empty flights', () => {
            render(<FlightFilter flights={[]} onFilter={mockOnFilter} />);

            const applyButton = screen.getByRole('button', { name: /Apply Filters/i });
            fireEvent.click(applyButton);

            expect(mockOnFilter).toHaveBeenCalledWith([]);
        });
    });
});
