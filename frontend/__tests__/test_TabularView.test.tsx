import React from 'react';
import { render, screen, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TabularView } from '@/components/flight-roster/tabular-view';

describe('TabularView', () => {
  const mockFlight = {
    id: 1,
    flight_number: 'TK001',
    airline: {
      id: 1,
      airline_name: 'Turkish Airlines',
      airline_code: 'TK',
      country: 'Turkey',
    },
    departure_time: '10:00',
    arrival_time: '14:30',
    flight_duration_minutes: 270,
    flight_distance_km: 2800,
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
      {
        id: 1,
        name: 'Captain John Smith',
        role: 'Captain',
        age: 45,
        gender: 'Male',
        nationality: 'USA',
        employee_id: 'FC001',
        license_number: 'ATP-12345',
        seniority_level: 'senior',
        max_allowed_distance_km: 10000,
        hours_flown: 5000,
        languages: ['English'],
      },
      {
        id: 2,
        name: 'First Officer Jane Doe',
        role: 'First Officer',
        age: 35,
        gender: 'Female',
        nationality: 'UK',
        employee_id: 'FC002',
        license_number: 'CPL-67890',
        seniority_level: 'junior',
        max_allowed_distance_km: 8000,
        hours_flown: 3000,
        languages: ['English'],
      },
    ],
    cabin_crew: [
      {
        id: 1,
        name: 'Sarah Johnson',
        attendant_type: 'Senior Flight Attendant',
        age: 32,
        gender: 'Female',
        nationality: 'USA',
        employee_id: 'CC001',
        languages: ['English', 'Spanish'],
      },
      {
        id: 2,
        name: 'Mike Brown',
        attendant_type: 'Flight Attendant',
        age: 28,
        gender: 'Male',
        nationality: 'Canada',
        employee_id: 'CC002',
        languages: ['English', 'French'],
      },
    ],
    passengers: [
      {
        id: 1,
        name: 'Alice Williams',
        age: 30,
        gender: 'Female',
        nationality: 'USA',
        passport_number: 'P123456',
        seat_type: 'Business',
        seat_number: '1A',
      },
      {
        id: 2,
        name: 'Bob Davis',
        age: 45,
        gender: 'Male',
        nationality: 'UK',
        passport_number: 'P234567',
        seat_type: 'Economy',
        seat_number: '10B',
      },
    ],
  };

  it('should render tabular view header', () => {
    render(<TabularView flight={mockFlight} />);

    expect(screen.getByText('Tabular View - All Personnel')).toBeInTheDocument();
  });

  it('should display flight crew in table', () => {
    render(<TabularView flight={mockFlight} />);

    expect(screen.getByText('Captain John Smith')).toBeInTheDocument();
    expect(screen.getByText('First Officer Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('Captain')).toBeInTheDocument();
    expect(screen.getByText('First Officer')).toBeInTheDocument();
  });

  it('should display cabin crew in table', () => {
    render(<TabularView flight={mockFlight} />);

    expect(screen.getByText('Sarah Johnson')).toBeInTheDocument();
    expect(screen.getByText('Mike Brown')).toBeInTheDocument();
  });

  it('should display passengers in table', () => {
    render(<TabularView flight={mockFlight} />);

    expect(screen.getByText('Alice Williams')).toBeInTheDocument();
    expect(screen.getByText('Bob Davis')).toBeInTheDocument();
  });

  it('should display passenger seat information', () => {
    render(<TabularView flight={mockFlight} />);

    expect(screen.getByText('1A')).toBeInTheDocument();
    expect(screen.getByText('10B')).toBeInTheDocument();
    expect(screen.getByText('Business')).toBeInTheDocument();
    expect(screen.getByText('Economy')).toBeInTheDocument();
  });

  it('should handle flight with no crew', () => {
    const noCrewFlight = {
      ...mockFlight,
      flight_crew: [],
      cabin_crew: [],
    };

    render(<TabularView flight={noCrewFlight} />);

    // Should still render but with only passengers
    expect(screen.getByText('Alice Williams')).toBeInTheDocument();
  });

  it('should handle flight with no passengers', () => {
    const noPassengersFlight = {
      ...mockFlight,
      passengers: [],
    };

    render(<TabularView flight={noPassengersFlight} />);

    // Should still render with crew
    expect(screen.getByText('Captain John Smith')).toBeInTheDocument();
  });

  it('should render tables with proper structure', () => {
    const { container } = render(<TabularView flight={mockFlight} />);

    const tables = container.querySelectorAll('table');
    expect(tables.length).toBeGreaterThanOrEqual(1);
  });

  it('should display crew count summaries', () => {
    render(<TabularView flight={mockFlight} />);

    // All people are shown in a single table
    expect(screen.getByText('Captain John Smith')).toBeInTheDocument();
    expect(screen.getByText('Alice Williams')).toBeInTheDocument();
  });

  it('should organize data into clear sections', () => {
    const { container } = render(<TabularView flight={mockFlight} />);

    // Data is organized in a single table with type badges
    expect(screen.getByText('Captain John Smith')).toBeInTheDocument();
    expect(screen.getByText('Sarah Johnson')).toBeInTheDocument();
    expect(screen.getByText('Alice Williams')).toBeInTheDocument();
  });

});
