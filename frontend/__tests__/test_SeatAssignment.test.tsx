import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SeatAssignment } from '@/components/flight-roster/seat-assignment';

const mockFlight = {
    id: 1,
    flight_number: 'TK001',
    vehicle_type: {
        id: 1,
        aircraft_name: 'Boeing 737',
        aircraft_code: 'B737',
        total_seats: 180,
        seating_plan: {
            business: 24,
            economy: 156,
            rows: 30,
            seats_per_row: 6,
        },
        max_crew: 10,
        max_passengers: 180,
    },
    flight_crew: [
        {
            id: 1,
            name: 'Captain Smith',
            seat_number: 'CREW1',
        },
    ],
    cabin_crew: [
        {
            id: 10,
            name: 'Sarah Attendant',
            seat_number: null,
        },
    ],
    passengers: [
        {
            id: 100,
            name: 'John Doe',
            seat_number: null,
            seat_type: 'economy',
        },
        {
            id: 101,
            name: 'Jane Smith',
            seat_number: '2A',
            seat_type: 'business',
        },
    ],
};

describe('SeatAssignment', () => {
    const mockOnSeatsAssigned = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('should render seat assignment component', () => {
            render(
                <SeatAssignment
                    flight={mockFlight}
                    onSeatsAssigned={mockOnSeatsAssigned}
                />
            );

            expect(screen.getByText(/Interactive Seat Map/i)).toBeInTheDocument();
        });

        it('should display flight number', () => {
            render(
                <SeatAssignment
                    flight={mockFlight}
                    onSeatsAssigned={mockOnSeatsAssigned}
                />
            );

            expect(screen.getByText(/TK001/)).toBeInTheDocument();
        });

        it('should display unassigned passengers', () => {
            render(
                <SeatAssignment
                    flight={mockFlight}
                    onSeatsAssigned={mockOnSeatsAssigned}
                />
            );

            expect(screen.getByText('John Doe')).toBeInTheDocument();
        });

        it('should display assigned passengers', () => {
            render(
                <SeatAssignment
                    flight={mockFlight}
                    onSeatsAssigned={mockOnSeatsAssigned}
                />
            );

            expect(screen.getByText('Jane Smith')).toBeInTheDocument();
        });
    });

    describe('Seating Plan', () => {
        it('should render seat grid with buttons', () => {
            render(
                <SeatAssignment
                    flight={mockFlight}
                    onSeatsAssigned={mockOnSeatsAssigned}
                />
            );

            // Should have multiple seat labels (e.g. 1A, 1B, etc)
            const seat1A = screen.getAllByText(/1A/i);
            expect(seat1A.length).toBeGreaterThan(0);
        });
    });

    describe('Initial Assignments', () => {
        it('should handle initial seat assignments', () => {
            const initialAssignments = { 100: '10A' };

            render(
                <SeatAssignment
                    flight={mockFlight}
                    onSeatsAssigned={mockOnSeatsAssigned}
                    initialAssignments={initialAssignments}
                />
            );

            expect(screen.getByText(/Interactive Seat Map/i)).toBeInTheDocument();
        });
    });

    describe('Empty State', () => {
        it('should handle flight with no passengers', () => {
            const flightWithNoPassengers = {
                ...mockFlight,
                passengers: [],
            };

            render(
                <SeatAssignment
                    flight={flightWithNoPassengers}
                    onSeatsAssigned={mockOnSeatsAssigned}
                />
            );

            expect(screen.getByText(/Interactive Seat Map/i)).toBeInTheDocument();
        });
    });
});
