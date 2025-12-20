/**
 * FlightStatistics Tests
 * Tests for flight statistics display component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { FlightStatistics } from '@/components/flight-roster/flight-statistics';

describe('FlightStatistics', () => {
  const mockFlight = {
    id: 1,
    flight_number: 'TK001',
    airline: {
      id: 1,
      airline_code: 'TK',
      airline_name: 'Turkish Airlines',
      country: 'Turkey',
    },
    departure_time: '10:00',
    arrival_time: '14:30',
    flight_duration_minutes: 270,
    flight_distance_km: 2800,
    departure_airport: {
      id: 1,
      airport_code: 'IST',
      airport_name: 'Istanbul Airport',
      city: 'Istanbul',
      country: 'Turkey',
    },
    arrival_airport: {
      id: 2,
      airport_code: 'LHR',
      airport_name: 'London Heathrow',
      city: 'London',
      country: 'UK',
    },
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
    status: 'scheduled',
    flight_crew: [
      { id: 1, name: 'Captain John Smith', role: 'Captain', age: 45, gender: 'Male', nationality: 'USA', employee_id: 'FC001', license_number: 'ATP-12345', seniority_level: 'senior', max_allowed_distance_km: 10000, hours_flown: 5000, languages: ['English'] },
      { id: 2, name: 'First Officer Jane Doe', role: 'First Officer', age: 35, gender: 'Female', nationality: 'UK', employee_id: 'FC002', license_number: 'CPL-67890', seniority_level: 'junior', max_allowed_distance_km: 8000, hours_flown: 3000, languages: ['English'] },
    ],
    cabin_crew: [
      { id: 1, name: 'Sarah Johnson', attendant_type: 'Senior', age: 32, gender: 'Female', nationality: 'USA', employee_id: 'CC001', languages: ['English', 'Spanish'] },
      { id: 2, name: 'Mike Brown', attendant_type: 'Junior', age: 28, gender: 'Male', nationality: 'Canada', employee_id: 'CC002', languages: ['English', 'French'] },
      { id: 3, name: 'Lisa Davis', attendant_type: 'Junior', age: 26, gender: 'Female', nationality: 'USA', employee_id: 'CC003', languages: ['English'] },
    ],
    passengers: [
      { id: 1, name: 'Alice Williams', seat_type: 'business', age: 30, gender: 'Female', nationality: 'USA', passport_number: 'P123456' },
      { id: 2, name: 'Bob Davis', seat_type: 'business', age: 45, gender: 'Male', nationality: 'UK', passport_number: 'P234567' },
      { id: 3, name: 'Charlie Evans', seat_type: 'economy', age: 28, gender: 'Male', nationality: 'Canada', passport_number: 'P345678' },
      { id: 4, name: 'Diana Foster', seat_type: 'economy', age: 35, gender: 'Female', nationality: 'USA', passport_number: 'P456789' },
      { id: 5, name: 'Eve Garcia', seat_type: 'economy', age: 42, gender: 'Female', nationality: 'Spain', passport_number: 'P567890' },
    ],
  };

  it('should display crew statistics', () => {
    render(<FlightStatistics flight={mockFlight} />);

    // Total crew is displayed
    expect(screen.getByText('Total Crew')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument(); // 2 flight crew + 3 cabin crew
  });

  it('should display passenger statistics', () => {
    render(<FlightStatistics flight={mockFlight} />);

    expect(screen.getByText('Overall Occupancy')).toBeInTheDocument();
    expect(screen.getByText('5/180')).toBeInTheDocument();
  });

  it('should display business class statistics', () => {
    render(<FlightStatistics flight={mockFlight} />);

    expect(screen.getByText('Business Class')).toBeInTheDocument();
    expect(screen.getByText(/2\/24|2\/16/)).toBeInTheDocument(); // 2 business passengers out of capacity
  });

  it('should display economy class statistics', () => {
    render(<FlightStatistics flight={mockFlight} />);

    expect(screen.getByText('Economy Class')).toBeInTheDocument();
    expect(screen.getByText(/3\/156|3\/150/)).toBeInTheDocument(); // 3 economy passengers out of capacity
  });

  it('should handle flight with no passengers', () => {
    const emptyFlight = {
      ...mockFlight,
      passengers: [],
    };

    render(<FlightStatistics flight={emptyFlight} />);

    expect(screen.getByText('Overall Occupancy')).toBeInTheDocument();
    expect(screen.getByText('0/180')).toBeInTheDocument();
  });

  it('should display available seats count', () => {
    render(<FlightStatistics flight={mockFlight} />);

    const availableSeats = 180 - 5; // total - passengers
    expect(screen.getByText('Available Seats:')).toBeInTheDocument();
    expect(screen.getByText(availableSeats.toString())).toBeInTheDocument();
  });

  it('should display crew composition correctly', () => {
    render(<FlightStatistics flight={mockFlight} />);

    // Should show total crew count  
    expect(screen.getByText('Total Crew')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('should render statistics in card layout', () => {
    const { container } = render(<FlightStatistics flight={mockFlight} />);

    // Check for card structure
    expect(container.querySelector('.space-y-4, .grid')).toBeInTheDocument();
  });
});
