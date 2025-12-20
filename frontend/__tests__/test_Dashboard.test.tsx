import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import FlightRosterDashboard from '@/components/flight-roster/dashboard';
import { useAuth } from '@/contexts/AuthContext';

// Mock Lucide icons to avoid rendering issues
jest.mock('lucide-react', () => ({
  Plane: () => <div data-testid="plane-icon" />,
  LayoutGrid: () => <div data-testid="layout-grid-icon" />,
  Database: () => <div data-testid="database-icon" />,
  Download: () => <div data-testid="download-icon" />,
  LogOut: () => <div data-testid="logout-icon" />,
  Search: () => <div data-testid="search-icon" />,
  Loader2: () => <div data-testid="loader-icon" className="animate-spin" />,
  Users: () => <div data-testid="users-icon" />,
  CheckCircle2: () => <div data-testid="check-circle-icon" />,
  Table2: () => <div data-testid="table-icon" />,
  BarChart3: () => <div data-testid="barchart-icon" />,
  X: () => <div data-testid="x-icon" />,
  Filter: () => <div data-testid="filter-icon" />,
  Calendar: () => <div data-testid="calendar-icon" />,
  MapPin: () => <div data-testid="mappin-icon" />,
  Building2: () => <div data-testid="building-icon" />,
  Clock: () => <div data-testid="clock-icon" />,
}));

// Mock AUth Context
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

// Mock sub-components to isolate Dashboard logic
jest.mock('@/components/flight-roster/flight-selector', () => ({
  FlightSelector: ({ onFlightSelect }: any) => (
    <div data-testid="flight-selector">
      <button onClick={() => onFlightSelect({ id: 1, flight_number: 'TK001' })}>Select Flight 1</button>
    </div>
  ),
}));

jest.mock('@/components/flight-roster/tabular-view', () => ({
  TabularView: () => <div data-testid="tabular-view">Tabular View</div>,
}));

jest.mock('@/components/flight-roster/plane-view', () => ({
  PlaneView: () => <div data-testid="plane-view">Plane View</div>,
}));

jest.mock('@/components/flight-roster/extended-view', () => ({
  ExtendedView: () => <div data-testid="extended-view">Extended View</div>,
}));

jest.mock('@/components/flight-roster/flight-statistics', () => ({
  FlightStatistics: () => <div data-testid="flight-statistics">Flight Statistics</div>,
}));

jest.mock('@/components/flight-roster/crew-selector', () => ({
  CrewSelector: ({ onCrewSelected }: any) => (
    <div data-testid="crew-selector">
      <button onClick={() => onCrewSelected([1], [10])}>Confirm Crew</button>
    </div>
  ),
}));

jest.mock('@/components/auth/role-guard', () => ({
  FeatureGuard: ({ children }: any) => <div data-testid="feature-guard">{children}</div>,
}));

// Mock global fetch
global.fetch = jest.fn();

// Mock sessionStorage
const sessionStorageMock = (() => {
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
  };
})();

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

// Mock window.confirm and alert
window.confirm = jest.fn(() => true);
window.alert = jest.fn();

describe('FlightRosterDashboard', () => {
  const mockLogout = jest.fn();

  const mockFlights = [
    { id: 1, flight_number: 'TK123', airline: { airline_name: 'Turkish Airlines', airline_code: 'TK' }, departure_airport: { airport_code: 'IST' }, arrival_airport: { airport_code: 'LHR' } },
  ];

  const mockFlightDetails = {
    id: 1,
    flight_number: 'TK123',
    airline: { airline_name: 'Turkish Airlines', airline_code: 'TK' },
    departure_airport: { airport_code: 'IST' },
    arrival_airport: { airport_code: 'LHR' },
    vehicle_type: { aircraft_code: 'B737', total_seats: 180 },
    flight_crew: [{ id: 1, name: 'Capt. Smith' }],
    cabin_crew: [{ id: 10, name: 'Sarah A.' }],
    passengers: [{ id: 100, name: 'John Doe' }],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorageMock.clear();
    (useAuth as jest.Mock).mockReturnValue({ logout: mockLogout });

    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (url.endsWith('/flight-info/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockFlights),
        });
      }
      if (url.includes('/flight-info/1')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockFlightDetails),
        });
      }
      if (url.endsWith('/roster/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  it('should render dashboard and fetch flights on mount', async () => {
    render(<FlightRosterDashboard />);

    expect(screen.getByText(/Flight Roster Management/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/flight-info/'));
    });
  });

  it('should restore state from sessionStorage', async () => {
    sessionStorageMock.getItem.mockImplementation((key) => {
      if (key === 'dashboard_flights') return JSON.stringify(mockFlights);
      if (key === 'dashboard_active_view') return 'tabular';
      if (key === 'dashboard_selected_flight_id') return '1';
      if (key === 'dashboard_selected_flight_data') return JSON.stringify(mockFlightDetails);
      return null;
    });

    render(<FlightRosterDashboard />);

    await waitFor(() => {
      expect(screen.getByTestId('tabular-view')).toBeInTheDocument();
    });
  });

  it('should handle flight selection', async () => {
    render(<FlightRosterDashboard />);

    await waitFor(() => {
      expect(screen.getByTestId('flight-selector')).toBeInTheDocument();
    });

    const selectButton = screen.getByText('Select Flight 1');
    fireEvent.click(selectButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/flight-info/1'));
    });
  });

  it('should switch between views', async () => {
    render(<FlightRosterDashboard />);

    // Default view is statistics
    await waitFor(() => {
      expect(screen.getByTestId('flight-statistics')).toBeInTheDocument();
    });

    // Switch to tabular
    const tabularTab = screen.getByRole('tab', { name: /Tabular/i });
    fireEvent.click(tabularTab);
    expect(screen.getByTestId('tabular-view')).toBeInTheDocument();

    // Switch to plane view
    const planeTab = screen.getByRole('tab', { name: /Plane/i });
    fireEvent.click(planeTab);
    expect(screen.getByTestId('plane-view')).toBeInTheDocument();
  });

  it('should open and handle Generate Roster dialog', async () => {
    // Select a flight first to show the Generate Roster button
    sessionStorageMock.getItem.mockImplementation((key) => {
      if (key === 'dashboard_selected_flight_data') return JSON.stringify(mockFlightDetails);
      if (key === 'dashboard_selected_flight_id') return '1';
      return null;
    });

    render(<FlightRosterDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Generate Roster/i)).toBeInTheDocument();
    });

    const generateButton = screen.getByText(/Generate Roster/i);
    fireEvent.click(generateButton);

    expect(screen.getByText(/Generate Flight Roster/i)).toBeInTheDocument();

    // Select NoSQL database
    const noSqlButton = screen.getByText('NoSQL');
    fireEvent.click(noSqlButton);

    // Mock successful generation
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: 'rost123', generated_at: new Date().toISOString() }),
    });

    const confirmButton = screen.getByText(/Generate & Save Roster/i);
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/roster/generate'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('"database_type":"nosql"'),
        })
      );
    });
  });

  it('should handle manual crew selection', async () => {
    sessionStorageMock.getItem.mockImplementation((key) => {
      if (key === 'dashboard_selected_flight_data') return JSON.stringify(mockFlightDetails);
      if (key === 'dashboard_selected_flight_id') return '1';
      return null;
    });

    render(<FlightRosterDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Generate Roster/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Generate Roster/i));

    const manualButton = screen.getByText('Manual');
    fireEvent.click(manualButton);

    // Should open crew selector dialog
    expect(screen.getByTestId('crew-selector')).toBeInTheDocument();

    const confirmCrewButton = screen.getByText('Confirm Crew');
    fireEvent.click(confirmCrewButton);

    // Dialog should stay open for roster generation confirm
    expect(screen.getByText(/Generate Flight Roster/i)).toBeInTheDocument();

    // Confirm generation
    fireEvent.click(screen.getByText(/Generate & Save Roster/i));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/roster/generate'),
        expect.objectContaining({
          body: expect.stringContaining('"auto_select_crew":false'),
        })
      );
    });
  });

  it('should open and handle Saved Rosters dialog', async () => {
    const mockRosters = [
      { id: 1, roster_name: 'Roster 1', generated_at: new Date().toISOString(), database_type: 'sql' },
    ];

    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (url.endsWith('/roster/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRosters),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    sessionStorageMock.getItem.mockImplementation((key) => {
      if (key === 'dashboard_selected_flight_data') return JSON.stringify(mockFlightDetails);
      if (key === 'dashboard_selected_flight_id') return '1';
      return null;
    });

    render(<FlightRosterDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/View Saved Rosters/i)).toBeInTheDocument();
    });

    const viewRostersButton = screen.getByText(/View Saved Rosters/i);
    fireEvent.click(viewRostersButton);

    await waitFor(() => {
      expect(screen.getByText('Saved Rosters')).toBeInTheDocument();
      expect(screen.getByText('Roster 1')).toBeInTheDocument();
    });
  });

  it('should handle export options', async () => {
    sessionStorageMock.getItem.mockImplementation((key) => {
      if (key === 'dashboard_selected_flight_data') return JSON.stringify(mockFlightDetails);
      if (key === 'dashboard_selected_flight_id') return '1';
      return null;
    });

    render(<FlightRosterDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/^Export$/i)).toBeInTheDocument();
    });

    const exportButton = screen.getByText(/^Export$/i);
    fireEvent.click(exportButton);

    expect(screen.getByText(/Export Flight Roster/i)).toBeInTheDocument();

    // Mock URL.createObjectURL and click
    const mockUrl = 'blob:test';
    window.URL.createObjectURL = jest.fn(() => mockUrl);
    window.URL.revokeObjectURL = jest.fn();

    const dlink = { click: jest.fn() };
    const originalCreateElement = document.createElement;
    document.createElement = jest.fn().mockImplementation((tag) => {
      if (tag === 'a') return dlink;
      return originalCreateElement.call(document, tag);
    });

    const confirmExportButton = screen.getByText(/Export JSON/i);
    fireEvent.click(confirmExportButton);

    expect(window.alert).toHaveBeenCalledWith(expect.stringContaining('Export successful'));

    document.createElement = originalCreateElement;
  });

  it('should handle logout', async () => {
    sessionStorageMock.getItem.mockImplementation((key) => {
      if (key === 'dashboard_selected_flight_data') return JSON.stringify(mockFlightDetails);
      if (key === 'dashboard_selected_flight_id') return '1';
      return null;
    });

    render(<FlightRosterDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Logout/i)).toBeInTheDocument();
    });

    const logoutButton = screen.getByText(/Logout/i);
    fireEvent.click(logoutButton);

    expect(mockLogout).toHaveBeenCalled();
  });
});
