import React from 'react';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CrewSelector } from '@/components/flight-roster/crew-selector';

// Mock fetch
global.fetch = jest.fn();

describe('CrewSelector', () => {
  const mockOnCrewSelected = jest.fn();

  const mockFlightCrew = [
    { id: 1, name: 'Capt. Alpha', role: 'Captain', seniority_level: 'Senior', qualified: true, age: 45, nationality: 'TR', license_number: 'L1', languages: ['EN'] },
    { id: 2, name: 'FO Beta', role: 'First Officer', seniority_level: 'Junior', qualified: true, age: 30, nationality: 'TR', license_number: 'L2', languages: ['EN'] },
    { id: 3, name: 'FO Gamma', role: 'First Officer', seniority_level: 'Trainee', qualified: true, age: 25, nationality: 'TR', license_number: 'L3', languages: ['EN'] },
  ];

  const mockCabinCrew = [
    { id: 10, name: 'Sarah Chief', attendant_type: 'chief', qualified: true, age: 35, nationality: 'US', employee_id: 'C1', languages: ['EN'] },
    { id: 11, name: 'Jack Regular', attendant_type: 'regular', qualified: true, age: 28, nationality: 'CA', employee_id: 'C2', languages: ['EN'] },
    { id: 12, name: 'Chef Mario', attendant_type: 'chef', qualified: true, age: 40, nationality: 'IT', employee_id: 'C3', languages: ['EN'], recipes: ['Pasta'] },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('/available-flight-crew/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockFlightCrew) });
      }
      if (url.includes('/available-cabin-crew/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockCabinCrew) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    });
  });

  afterEach(() => {
    cleanup();
  });

  it('should render and fetch crew on mount', async () => {
    render(<CrewSelector flightId={1} onCrewSelected={mockOnCrewSelected} />);

    expect(screen.getByText(/Loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Capt. Alpha')).toBeInTheDocument();
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });

  it('should handle flight crew selection and validation', async () => {
    render(<CrewSelector flightId={1} onCrewSelected={mockOnCrewSelected} />);

    await waitFor(() => {
      expect(screen.getByText('Capt. Alpha')).toBeInTheDocument();
    });

    // Initially should show validation errors (missing First Officer etc)
    expect(screen.getByText(/Must select at least one Captain/i)).toBeInTheDocument();

    // Toggle Captain selection
    const captainCard = screen.getByText('Capt. Alpha').closest('.cursor-pointer');
    if (captainCard) fireEvent.click(captainCard);

    await waitFor(() => {
      expect(screen.queryByText(/Must select at least one Captain/i)).not.toBeInTheDocument();
      expect(screen.getByText(/Must select at least one First Officer/i)).toBeInTheDocument();
    });

    expect(mockOnCrewSelected).toHaveBeenCalled();
  });

  it('should handle cabin crew selection', async () => {
    render(<CrewSelector flightId={1} onCrewSelected={mockOnCrewSelected} />);

    await waitFor(() => {
      expect(screen.getByText('Cabin Crew')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Cabin Crew/i));

    await waitFor(() => {
      expect(screen.getByText('Sarah Chief')).toBeInTheDocument();
    });

    const chiefCard = screen.getByText('Sarah Chief').closest('.cursor-pointer');
    if (chiefCard) fireEvent.click(chiefCard);

    expect(mockOnCrewSelected).toHaveBeenCalled();
  });

  it('should handle Quick Select', async () => {
    render(<CrewSelector flightId={1} onCrewSelected={mockOnCrewSelected} />);

    await waitFor(() => {
      expect(screen.getByText(/Quick Select/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Quick Select Recommended/i));

    await waitFor(() => {
      // Should have called onCrewSelected with multiple IDs
      expect(mockOnCrewSelected).toHaveBeenCalledWith(
        expect.arrayContaining([1, 2]), // Alpha and Beta (Captain and FO)
        expect.arrayContaining([10, 11, 12]) // Chief, Regular, Chef
      );
    });
  });

  it('should handle Clear All', async () => {
    render(<CrewSelector flightId={1} onCrewSelected={mockOnCrewSelected} />);

    await waitFor(() => {
      expect(screen.getByText('Capt. Alpha')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Capt. Alpha'));
    expect(mockOnCrewSelected).toHaveBeenLastCalledWith(expect.arrayContaining([1]), expect.anything());

    fireEvent.click(screen.getByText(/Clear All/i));

    await waitFor(() => {
      expect(mockOnCrewSelected).toHaveBeenLastCalledWith([], []);
    });
  });

  it('should prevent selection of unqualified crew', async () => {
    const unqualifiedCrew = [
      { id: 99, name: 'Unqualified Pilot', role: 'Captain', seniority_level: 'Senior', qualified: false, age: 45, nationality: 'TR', license_number: 'L99', languages: ['EN'] },
    ];

    (global.fetch as jest.Mock).mockReturnValueOnce(
      Promise.resolve({ ok: true, json: () => Promise.resolve(unqualifiedCrew) })
    );

    render(<CrewSelector flightId={1} onCrewSelected={mockOnCrewSelected} />);

    await waitFor(() => {
      expect(screen.getByText('Unqualified Pilot')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Unqualified Pilot'));

    // Should NOT be selected
    expect(mockOnCrewSelected).not.toHaveBeenCalledWith(expect.arrayContaining([99]), expect.anything());
  });
});
