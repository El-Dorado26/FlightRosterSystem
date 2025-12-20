import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ExtendedView } from '@/components/flight-roster/extended-view';

const mockFlight = {
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
        seating_plan: {},
        max_crew: 10,
        max_passengers: 180,
    },
    status: 'scheduled',
    flight_crew: [
        {
            id: 1,
            name: 'Captain Smith',
            role: 'Captain',
            seniority_level: 'Senior',
            age: 45,
            nationality: 'Turkish',
            license_number: 'PIL001',
            languages: [{ language: 'English' }, { language: 'Turkish' }],
        },
        {
            id: 2,
            name: 'First Officer Jones',
            role: 'First Officer',
            seniority_level: 'Junior',
            age: 32,
            nationality: 'American',
            license_number: 'PIL002',
            languages: [{ language: 'English' }],
        },
    ],
    cabin_crew: [
        {
            id: 10,
            name: 'Sarah Attendant',
            attendant_type: 'chief',
            languages: ['English', 'Turkish', 'German'],
            employee_id: 'CAB001',
            age: 35,
            nationality: 'Turkish',
            recipes: [],
        },
    ],
    passengers: [
        {
            id: 1,
            name: 'John Doe',
            age: 30,
            gender: 'Male',
            nationality: 'American',
            email: 'john@example.com',
            phone: '+1234567890',
            passport_number: 'PASS001',
            seat_number: '1A',
            seat_type: 'business',
            is_parent: false,
            parent_passenger_id: null,
        },
    ],
};

describe('ExtendedView', () => {
    describe('Rendering', () => {
        it('should render extended view component', () => {
            render(<ExtendedView flight={mockFlight} />);

            expect(screen.getByText(/Extended View/i)).toBeInTheDocument();
        });

        it('should display flight number in description', () => {
            render(<ExtendedView flight={mockFlight} />);

            expect(screen.getByText(/TK001/)).toBeInTheDocument();
        });
    });

    describe('Tabs', () => {
        it('should display Flight Crew tab', () => {
            render(<ExtendedView flight={mockFlight} />);

            expect(screen.getByRole('tab', { name: /Flight Crew/i })).toBeInTheDocument();
        });

        it('should display Cabin Crew tab', () => {
            render(<ExtendedView flight={mockFlight} />);

            expect(screen.getByRole('tab', { name: /Cabin Crew/i })).toBeInTheDocument();
        });

        it('should display Passengers tab', () => {
            render(<ExtendedView flight={mockFlight} />);

            expect(screen.getByRole('tab', { name: /Passengers/i })).toBeInTheDocument();
        });
    });

    describe('Flight Crew Section', () => {
        it('should display flight crew members', () => {
            render(<ExtendedView flight={mockFlight} />);

            expect(screen.getByText('Captain Smith')).toBeInTheDocument();
        });

        it('should display crew roles', () => {
            render(<ExtendedView flight={mockFlight} />);

            expect(screen.getByText('Captain')).toBeInTheDocument();
        });

        it('should display crew count in tab', () => {
            render(<ExtendedView flight={mockFlight} />);

            // The tab should show count in format "Flight Crew (2)"
            expect(screen.getByRole('tab', { name: /Flight Crew.*2/i })).toBeInTheDocument();
        });
    });

    describe('Empty State', () => {
        it('should handle flight with no crew', () => {
            const flightWithNoCrew = {
                ...mockFlight,
                flight_crew: [],
                cabin_crew: [],
            };

            render(<ExtendedView flight={flightWithNoCrew} />);

            // Should still render
            expect(screen.getByText(/Extended View/i)).toBeInTheDocument();
        });

        it('should handle flight with no passengers', async () => {
            const flightWithNoPassengers = {
                ...mockFlight,
                passengers: [],
            };

            render(<ExtendedView flight={flightWithNoPassengers} />);

            // Should still render
            expect(screen.getByText(/Extended View/i)).toBeInTheDocument();
        });
    });
});
