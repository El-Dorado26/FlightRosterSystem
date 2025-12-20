import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { FlightSearch } from '@/components/flight-roster/flight-search';

// Mock fetch
global.fetch = jest.fn();

describe('FlightSearch', () => {
  const mockOnSearch = jest.fn();
  const mockOnClear = jest.fn();

  const mockAirlines = [
    { id: 1, airline_name: 'Turkish Airlines', airline_code: 'TK' },
  ];

  const mockAirports = [
    { id: 1, airport_code: 'IST', airport_name: 'Istanbul Airport' },
    { id: 2, airport_code: 'LHR', airport_name: 'London Heathrow' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('/airlines')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAirlines),
        });
      }
      if (url.includes('/airports')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAirports),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
      });
    });
  });

  it('should render search component', () => {
    render(<FlightSearch onSearch={mockOnSearch} onClear={mockOnClear} />);
    expect(screen.getByText(/Flight Search/i)).toBeInTheDocument();
  });

  it('should toggle advanced filters', () => {
    render(<FlightSearch onSearch={mockOnSearch} onClear={mockOnClear} />);

    // Initially advanced filters are hidden
    expect(screen.queryByText(/Advanced Filters/i)).not.toBeInTheDocument();

    const toggleButton = screen.getByRole('button', { name: /Show Filters/i });
    fireEvent.click(toggleButton);

    expect(screen.getByText(/Advanced Filters/i)).toBeInTheDocument();
    expect(screen.getByText(/Hide Filters/i)).toBeInTheDocument();
  });

  it('should pass flight number filter to onSearch', async () => {
    render(<FlightSearch onSearch={mockOnSearch} onClear={mockOnClear} />);

    const flightNumberInput = screen.getByPlaceholderText(/AA2500/i);
    await userEvent.type(flightNumberInput, 'tk001');

    const searchButton = screen.getByRole('button', { name: /^Search$/i });
    fireEvent.click(searchButton);

    expect(mockOnSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        flightNumber: 'TK001',
      })
    );
  });

  it('should handle quick date presets', async () => {
    render(<FlightSearch onSearch={mockOnSearch} onClear={mockOnClear} />);

    const todayButton = screen.getByRole('button', { name: /Today/i });
    fireEvent.click(todayButton);

    // Should show advanced filters automatically
    expect(screen.getByText(/Advanced Filters/i)).toBeInTheDocument();

    const startDateInput = screen.getByLabelText(/Departure From/i) as HTMLInputElement;
    expect(startDateInput.value).not.toBe('');
  });

  it('should handle advanced filter inputs', async () => {
    render(<FlightSearch onSearch={mockOnSearch} onClear={mockOnClear} />);
    fireEvent.click(screen.getByRole('button', { name: /Show Filters/i }));

    // Type in country/city filters
    const fromCountry = screen.getByPlaceholderText(/e.g., USA, UK/i);
    await userEvent.type(fromCountry, 'Turkey');

    const distanceMin = screen.getByPlaceholderText(/Min/i);
    await userEvent.type(distanceMin, '500');

    fireEvent.click(screen.getByRole('button', { name: /Apply Filters/i }));

    expect(mockOnSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        sourceCountry: 'Turkey',
        minDistance: 500
      })
    );
  });

  it('should clear individual filters from chips', async () => {
    render(<FlightSearch onSearch={mockOnSearch} onClear={mockOnClear} />);

    const input = screen.getByPlaceholderText(/AA2500/i);
    await userEvent.type(input, 'TK123');
    fireEvent.click(screen.getByRole('button', { name: /^Search$/i }));

    // Should see active filter chip
    expect(screen.getByText(/Active Filters:/i)).toBeInTheDocument();
    expect(screen.getByText(/Flight: TK123/i)).toBeInTheDocument();

    // Click X on chip
    const clearChip = screen.getByText(/Flight: TK123/i).querySelector('svg');
    if (clearChip) fireEvent.click(clearChip);

    expect(input).toHaveValue('');
  });

  it('should clear all filters', async () => {
    render(<FlightSearch onSearch={mockOnSearch} onClear={mockOnClear} />);

    const input = screen.getByPlaceholderText(/AA2500/i);
    await userEvent.type(input, 'TK123');

    fireEvent.click(screen.getByRole('button', { name: /Show Filters/i }));
    const clearButton = screen.getByRole('button', { name: /Clear All/i });
    fireEvent.click(clearButton);

    expect(mockOnClear).toHaveBeenCalled();
    expect(input).toHaveValue('');
  });
});
