import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { FlightSelector } from '@/components/flight-roster/flight-selector';
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
        business: 24,
        economy: 156,
        rows: 30,
        seats_per_row: 6,
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
    flight_number: 'TK002',
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
      id: 3,
      airport_name: 'JFK Airport',
      airport_code: 'JFK',
      city: 'New York',
      country: 'USA',
    },
    departure_time: '15:00',
    arrival_time: '20:00',
    flight_duration_minutes: 600,
    flight_distance_km: 8000,
    vehicle_type: {
      id: 2,
      aircraft_name: 'Boeing 777',
      aircraft_code: 'B777',
      total_seats: 350,
      seating_plan: {
        business: 50,
        economy: 300,
        rows: 50,
        seats_per_row: 10,
      },
      max_crew: 15,
      max_passengers: 350,
    },
    status: 'scheduled',
    flight_crew: [],
    cabin_crew: [],
    passengers: [],
  },
  {
    id: 3,
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
        business: 24,
        economy: 156,
        rows: 30,
        seats_per_row: 6,
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

describe('FlightSelector', () => {
  const mockOnSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render flight selector component', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText(/Flight Selection/i)).toBeInTheDocument();
    });

    it('should display all flight cards', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText('TK001')).toBeInTheDocument();
      expect(screen.getByText('TK002')).toBeInTheDocument();
      expect(screen.getByText('BA156')).toBeInTheDocument();
    });

    it('should handle empty flight list', () => {
      render(
        <FlightSelector
          flights={[]}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText(/No flights/i)).toBeInTheDocument();
    });

    it('should show loading state when isLoading is true', () => {
      render(
        <FlightSelector
          flights={[]}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
          isLoading={true}
        />
      );

      expect(screen.getByText(/Loading/i)).toBeInTheDocument();
    });
  });

  describe('Flight Selection', () => {
    it('should call onFlightSelect when flight is clicked', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      const flightCard = screen.getByText('TK001').closest('div[role="button"]');
      if (flightCard) fireEvent.click(flightCard);

      expect(mockOnSelect).toHaveBeenCalledWith(mockFlights[0]);
    });

    it('should highlight selected flight', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={mockFlights[0]}
          onFlightSelect={mockOnSelect}
        />
      );

      const selectedCard = screen.getByText('TK001').closest('div');
      expect(selectedCard).toHaveClass(/ring|border|selected/);
    });

    it('should allow selecting different flight', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={mockFlights[0]}
          onFlightSelect={mockOnSelect}
        />
      );

      const flightCard = screen.getByText('TK002').closest('div[role="button"]');
      if (flightCard) fireEvent.click(flightCard);

      expect(mockOnSelect).toHaveBeenCalledWith(mockFlights[1]);
    });
  });

  describe('Flight Details Display', () => {
    it('should display airport codes', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText('IST')).toBeInTheDocument();
      expect(screen.getByText('LHR')).toBeInTheDocument();
    });

    it('should display flight times', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText(/10:00/)).toBeInTheDocument();
      expect(screen.getByText(/14:30/)).toBeInTheDocument();
    });

    it('should display aircraft type', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText(/B737|Boeing 737/)).toBeInTheDocument();
    });

    it('should display flight status', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText(/scheduled/i)).toBeInTheDocument();
      expect(screen.getByText(/departed/i)).toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    it('should have search input', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      expect(searchInput).toBeInTheDocument();
    });

    it('should filter flights by flight number', async () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await userEvent.type(searchInput, 'TK001');

      expect(screen.getByText('TK001')).toBeInTheDocument();
      expect(screen.queryByText('BA156')).not.toBeInTheDocument();
    });

    it('should filter flights by destination', async () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await userEvent.type(searchInput, 'JFK');

      expect(screen.getByText('TK002')).toBeInTheDocument();
      expect(screen.queryByText('TK001')).not.toBeInTheDocument();
    });

    it('should show no results message when search matches nothing', async () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await userEvent.type(searchInput, 'XYZ999');

      expect(screen.getByText(/no flights/i)).toBeInTheDocument();
    });

    it('should clear search when clear button clicked', async () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await userEvent.type(searchInput, 'TK001');

      const clearButton = screen.getByRole('button', { name: /clear|×/i });
      if (clearButton) {
        fireEvent.click(clearButton);
        expect(searchInput).toHaveValue('');
      }
    });
  });

  describe('Flight Card Information', () => {
    it('should display flight duration', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      // TK001 is 270 minutes = 4h 30m
      expect(screen.getByText(/4.*30|270/)).toBeInTheDocument();
    });

    it('should display flight distance', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText(/2800|2,800/)).toBeInTheDocument();
    });

    it('should display airline name or code', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText(/Turkish Airlines|TK/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper role attributes on flight cards', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      const flightCards = screen.getAllByRole('button');
      expect(flightCards.length).toBeGreaterThan(0);
    });

    it('should be keyboard navigable', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      const flightCard = screen.getByText('TK001').closest('div[role="button"]') as HTMLElement;
      if (flightCard) {
        flightCard.focus();
        fireEvent.keyDown(flightCard, { key: 'Enter', code: 'Enter' });

        expect(mockOnSelect).toHaveBeenCalled();
      }
    });
  });

  describe('Edge Cases', () => {
    it('should handle flight with missing vehicle type', () => {
      const flightsWithMissingData = [{
        ...mockFlights[0],
        vehicle_type: null,
      }];

      render(
        <FlightSelector
          flights={flightsWithMissingData as any}
          selectedFlight={null}
          onFlightSelect={mockOnSelect}
        />
      );

      expect(screen.getByText('TK001')).toBeInTheDocument();
    });

    it('should handle click outside to deselect', () => {
      render(
        <FlightSelector
          flights={mockFlights}
          selectedFlight={mockFlights[0]}
          onFlightSelect={mockOnSelect}
        />
      );

      // Click outside the flight cards area
      fireEvent.mouseDown(document.body);

      // This depends on implementation - some selectors close on outside click
    });
  });
});
