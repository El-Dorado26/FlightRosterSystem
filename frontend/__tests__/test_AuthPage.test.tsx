import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import AuthPage from '@/components/auth/auth-page';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

jest.mock('@/contexts/AuthContext');
jest.mock('next/navigation');

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;

describe('AuthPage', () => {
  const mockLogin = jest.fn();
  const mockRegister = jest.fn();
  const mockPush = jest.fn();
  const mockOnLogin = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      login: mockLogin,
      register: mockRegister,
      logout: jest.fn(),
      isAuthenticated: false,
      hasRole: jest.fn(),
    });

    mockUseRouter.mockReturnValue({
      push: mockPush,
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    } as any);
  });

  describe('Login Form', () => {
    it('should render login form by default', () => {
      render(<AuthPage onLogin={mockOnLogin} />);

      expect(screen.getByPlaceholderText(/admin@openairlines.com/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument();
    });

    it('should have sign in button', () => {
      render(<AuthPage onLogin={mockOnLogin} />);

      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });

    it('should show error when submitting empty login form', async () => {
      render(<AuthPage onLogin={mockOnLogin} />);

      const signInButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(signInButton);

      await waitFor(() => {
        expect(screen.getByText(/Please fill in all fields/i)).toBeInTheDocument();
      });
    });

    it('should call login with email and password', async () => {
      mockLogin.mockResolvedValue({});
      render(<AuthPage onLogin={mockOnLogin} />);

      const emailInput = screen.getByPlaceholderText(/admin@openairlines.com/i);
      const passwordInput = screen.getByPlaceholderText(/enter your password/i);

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');

      const signInButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(signInButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
      });
    });

    it('should show error message on login failure', async () => {
      mockLogin.mockRejectedValue(new Error('Invalid credentials'));
      render(<AuthPage onLogin={mockOnLogin} />);

      const emailInput = screen.getByPlaceholderText(/admin@openairlines.com/i);
      const passwordInput = screen.getByPlaceholderText(/enter your password/i);

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');

      const signInButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(signInButton);

      await waitFor(() => {
        expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
      });
    });

    it('should call onLogin callback after successful login', async () => {
      mockLogin.mockResolvedValue({});
      render(<AuthPage onLogin={mockOnLogin} />);

      const emailInput = screen.getByPlaceholderText(/admin@openairlines.com/i);
      const passwordInput = screen.getByPlaceholderText(/enter your password/i);

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');

      fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(mockOnLogin).toHaveBeenCalled();
      });
    });
  });

  describe('Signup Form', () => {
    it('should have signup tab', () => {
      render(<AuthPage onLogin={mockOnLogin} />);
      expect(screen.getByRole('tab', { name: /sign up/i })).toBeInTheDocument();
    });

    it('should switch to signup tab on click', () => {
      render(<AuthPage onLogin={mockOnLogin} />);
      const signUpTab = screen.getByRole('tab', { name: /sign up/i });
      fireEvent.click(signUpTab);

      // Signup form should now be visible - check for Create Account button
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
    });
  });

  describe('Branding Section', () => {
    it('should display branding elements', () => {
      render(<AuthPage onLogin={mockOnLogin} />);

      expect(screen.getByText('OpenAIrlines')).toBeInTheDocument();
    });

    it('should display feature list', () => {
      render(<AuthPage onLogin={mockOnLogin} />);

      expect(screen.getByText('Real-time Flight Roster')).toBeInTheDocument();
      expect(screen.getByText('Interactive Seat Maps')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should have tab to switch to register', () => {
      render(<AuthPage onLogin={mockOnLogin} />);

      expect(screen.getByRole('tab', { name: /sign up/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /login/i })).toBeInTheDocument();
    });
  });
});
