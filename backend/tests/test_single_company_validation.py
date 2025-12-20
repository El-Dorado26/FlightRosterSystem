"""
Test single company constraint validation.

This test verifies that the Flight Information API enforces single-company operations,
where all flight numbers must start with the same airline code (PRIMARY_AIRLINE_CODE).
"""

import pytest
from fastapi import HTTPException
from api.routes.flights import _validate_single_company_operation
import os


class TestSingleCompanyValidation:
    """Test suite for single company operation validation."""

    def test_valid_flight_number_with_primary_airline(self):
        """Test that flight numbers matching PRIMARY_AIRLINE_CODE pass validation."""
        # Set PRIMARY_AIRLINE_CODE for testing
        primary_code = os.getenv("PRIMARY_AIRLINE_CODE", "TK")

        # Valid flight numbers starting with TK
        valid_flight_numbers = [
            f"{primary_code}0001",
            f"{primary_code}0002",
            f"{primary_code}9999",
            f"{primary_code}1234",
        ]

        for flight_number in valid_flight_numbers:
            # Should not raise any exception
            _validate_single_company_operation(flight_number)

    def test_invalid_flight_number_with_different_airline(self):
        """Test that flight numbers NOT matching PRIMARY_AIRLINE_CODE are rejected."""
        primary_code = os.getenv("PRIMARY_AIRLINE_CODE", "TK")

        # Invalid flight numbers with different airline codes
        invalid_flight_numbers = [
            "BA0001",  # British Airways
            "LH0002",  # Lufthansa
            "AF0003",  # Air France
            "EK0004",  # Emirates
        ]

        for flight_number in invalid_flight_numbers:
            if flight_number[:2] != primary_code:
                with pytest.raises(HTTPException) as exc_info:
                    _validate_single_company_operation(flight_number)

                # Verify error details
                assert exc_info.value.status_code == 400
                assert primary_code in exc_info.value.detail
                assert "single-company" in exc_info.value.detail.lower()
                assert flight_number[:2] in exc_info.value.detail

    def test_validation_message_clarity(self):
        """Test that validation error message is clear and informative."""
        primary_code = os.getenv("PRIMARY_AIRLINE_CODE", "TK")

        with pytest.raises(HTTPException) as exc_info:
            _validate_single_company_operation("BA1234")

        error_message = exc_info.value.detail

        # Verify message contains key information
        assert primary_code in error_message
        assert "BA" in error_message
        assert "single-company" in error_message.lower()
        assert exc_info.value.status_code == 400

    def test_case_sensitivity(self):
        """Test that validation works with uppercase flight numbers."""
        primary_code = os.getenv("PRIMARY_AIRLINE_CODE", "TK")

        # Uppercase should work (standard format)
        _validate_single_company_operation(f"{primary_code}0001")

        # Test with different airline code
        with pytest.raises(HTTPException):
            _validate_single_company_operation("BA0001")


class TestPrimaryAirlineCodeConfiguration:
    """Test that PRIMARY_AIRLINE_CODE is properly configured."""

    def test_primary_airline_code_is_set(self):
        """Verify PRIMARY_AIRLINE_CODE environment variable exists."""
        from api.routes.flights import PRIMARY_AIRLINE_CODE

        assert PRIMARY_AIRLINE_CODE is not None
        assert len(PRIMARY_AIRLINE_CODE) == 2
        assert PRIMARY_AIRLINE_CODE.isupper()

    def test_primary_airline_code_format(self):
        """Verify PRIMARY_AIRLINE_CODE is in correct format (2 uppercase letters)."""
        from api.routes.flights import PRIMARY_AIRLINE_CODE

        assert len(PRIMARY_AIRLINE_CODE) == 2
        assert PRIMARY_AIRLINE_CODE.isalpha()
        assert PRIMARY_AIRLINE_CODE.isupper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
