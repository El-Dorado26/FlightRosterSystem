import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PlaneView } from '@/components/flight-roster/plane-view';

describe('PlaneView', () => {
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
        rows: 30,
        seats_per_row: 6,
        business: 24,
        economy: 156,
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
        seat_number: 'COCKPIT-L',
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
        seat_number: null,
      },
    ],
    cabin_crew: [
      {
        id: 1,
        name: 'Sarah Johnson',
        attendant_type: 'Senior',
        age: 32,
        gender: 'Female',
        nationality: 'USA',
        employee_id: 'CC001',
        languages: ['English', 'Spanish'],
        seat_number: 'CC1',
      },
      {
        id: 2,
        name: 'Mike Brown',
        attendant_type: 'Junior',
        age: 28,
        gender: 'Male',
        nationality: 'Canada',
        employee_id: 'CC002',
        languages: ['English', 'French'],
        seat_number: 'CC2',
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
        seat_number: '1A',
        seat_type: 'Business',
      },
      {
        id: 2,
        name: 'Bob Davis',
        age: 45,
        gender: 'Male',
        nationality: 'UK',
        passport_number: 'P234567',
        seat_number: '10B',
        seat_type: 'Economy',
      },
      {
        id: 3,
        name: 'Charlie Evans',
        age: 28,
        gender: 'Male',
        nationality: 'Canada',
        passport_number: 'P345678',
        seat_number: null,
        seat_type: 'Economy',
      },
    ],
  };

  it('should render plane view with cockpit', () => {
    render(<PlaneView flight={mockFlight} />);

    expect(screen.getByText('Plane View - Seat Map')).toBeInTheDocument();
    expect(screen.getByText('COCKPIT')).toBeInTheDocument();
  });

  it('should display aircraft information', () => {
    render(<PlaneView flight={mockFlight} />);

    expect(screen.getByText(/Boeing 737/)).toBeInTheDocument();
    expect(screen.getByText(/B737/)).toBeInTheDocument();
  });

  it('should render crew area with crew members', () => {
    render(<PlaneView flight={mockFlight} />);

    expect(screen.getByText('CREW AREA')).toBeInTheDocument();

    // Flight crew should be displayed
    expect(screen.getByText('COCKPIT-L')).toBeInTheDocument();

    // Cabin crew should be displayed
    expect(screen.getByText('CC1')).toBeInTheDocument();
    expect(screen.getByText('CC2')).toBeInTheDocument();
  });

  it('should auto-assign labels for crew without seat numbers', () => {
    render(<PlaneView flight={mockFlight} />);

    // Second flight crew member without seat should get FC2
    expect(screen.getByText('FC2')).toBeInTheDocument();
  });

  it('should render business and economy class sections', () => {
    render(<PlaneView flight={mockFlight} />);

    expect(screen.getByText('BUSINESS CLASS')).toBeInTheDocument();
    expect(screen.getByText('ECONOMY CLASS')).toBeInTheDocument();
  });

  it('should show seat legend', () => {
    render(<PlaneView flight={mockFlight} />);

    expect(screen.getByText('Available')).toBeInTheDocument();
    expect(screen.getByText('Passenger')).toBeInTheDocument();
    expect(screen.getByText('Flight Crew')).toBeInTheDocument();
    expect(screen.getByText('Cabin Crew')).toBeInTheDocument();
  });

  it('should display seat statistics', () => {
    render(<PlaneView flight={mockFlight} />);

    expect(screen.getByText(/Total Seats:/)).toBeInTheDocument();
    expect(screen.getByText(/Occupied:/)).toBeInTheDocument();
    expect(screen.getByText(/Available:/)).toBeInTheDocument();
  });

  it('should show tooltip on seat hover', async () => {
    render(<PlaneView flight={mockFlight} />);

    // Find a passenger seat
    const seat1A = screen.getByText('1A');

    fireEvent.mouseEnter(seat1A);

    await waitFor(() => {
      expect(screen.getByText('Alice Williams')).toBeInTheDocument();
      expect(screen.getByText(/Type: Passenger/)).toBeInTheDocument();
    });
  });

  it('should hide tooltip on mouse leave', async () => {
    render(<PlaneView flight={mockFlight} />);

    const seat1A = screen.getByText('1A');

    fireEvent.mouseEnter(seat1A);
    await waitFor(() => {
      expect(screen.getByText('Alice Williams')).toBeInTheDocument();
    });

    fireEvent.mouseLeave(seat1A);

    await waitFor(() => {
      expect(screen.queryByText('Alice Williams')).not.toBeInTheDocument();
    });
  });

  it('should show crew tooltip with role information', async () => {
    render(<PlaneView flight={mockFlight} />);

    const crewSeat = screen.getByText('COCKPIT-L');

    fireEvent.mouseEnter(crewSeat);

    await waitFor(() => {
      expect(screen.getByText('Captain John Smith')).toBeInTheDocument();
      expect(screen.getByText(/Type: Flight Crew/)).toBeInTheDocument();
      expect(screen.getByText(/Role: Captain/)).toBeInTheDocument();
    });
  });

  it('should handle flight with no passengers', () => {
    const emptyFlight = {
      ...mockFlight,
      passengers: [],
    };

    render(<PlaneView flight={emptyFlight} />);

    expect(screen.getByText('Plane View - Seat Map')).toBeInTheDocument();
    expect(screen.getByText('COCKPIT')).toBeInTheDocument();
  });

  it('should handle flight with no crew', () => {
    const noCrewFlight = {
      ...mockFlight,
      flight_crew: [],
      cabin_crew: [],
    };

    render(<PlaneView flight={noCrewFlight} />);

    expect(screen.getByText('CREW AREA')).toBeInTheDocument();
  });

  it('should handle missing vehicle type gracefully', () => {
    const flightWithoutVehicle = {
      ...mockFlight,
      vehicle_type: {},
    };

    render(<PlaneView flight={flightWithoutVehicle as any} />);

    expect(screen.getByText('Plane View - Seat Map')).toBeInTheDocument();
  });

  it('should color code seats correctly', () => {
    const { container } = render(<PlaneView flight={mockFlight} />);

    // Check that different seat types have different colors (via CSS classes)
    const seat1A = screen.getByText('1A');
    const parentDiv = seat1A.parentElement;

    // Occupied passenger seat should have gray background
    expect(parentDiv?.className).toContain('bg-gray-400');
  });

  it('should not show crew members in passenger seating area', () => {
    render(<PlaneView flight={mockFlight} />);

    // Crew seats should only appear in crew area, not in passenger rows
    const allCockpitSeats = screen.getAllByText(/COCKPIT-L|FC2/);

    // Should only appear once in crew area
    expect(allCockpitSeats.length).toBe(2);
  });
});
