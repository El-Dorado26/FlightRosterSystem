#!/bin/bash
# Test runner script for Flight Roster System

set -e

echo "Flight Roster System - Test Suite"
echo "=================================="
echo ""

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must be run from the backend directory"
    exit 1
fi

# If second argument provided, run specific test
if [ -n "$2" ]; then
    echo "Running specific test: $2"
    pytest "tests/test_redis.py::$2" -v
    exit 0
fi

# Parse command line arguments
TEST_TYPE=${1:-all}

case $TEST_TYPE in
    all)
        echo "Running all tests..."
        pytest -v
        ;;
    unit)
        echo "Running unit tests only..."
        pytest -m unit -v
        ;;
    integration)
        echo "Running integration tests only..."
        pytest -m integration -v
        ;;
    redis)
        echo "Running all redis module tests..."
        pytest tests/test_redis.py -v
        ;;
    build-key)
        echo "Running build_cache_key tests..."
        pytest tests/test_redis.py::TestBuildCacheKey -v
        ;;
    set-cache)
        echo "Running set_cache tests..."
        pytest tests/test_redis.py::TestSetCache -v
        ;;
    get-cache)
        echo "Running get_cache tests..."
        pytest tests/test_redis.py::TestGetCache -v
        ;;
    delete-cache)
        echo "Running delete_cache tests..."
        pytest tests/test_redis.py::TestDeleteCache -v
        ;;
    clear-cache)
        echo "Running clear_cache tests..."
        pytest tests/test_redis.py::TestClearCache -v
        ;;
    exists)
        echo "Running exists tests..."
        pytest tests/test_redis.py::TestExists -v
        ;;
    roster-utils)
        echo "Running roster_utils tests..."
        pytest tests/test_roster_utils.py -v
        ;;
    integration)
        echo "Running API integration tests..."
        pytest tests/test_api_integration.py -v
        ;;
    equivalence)
        echo "Running equivalence partitioning and BVA tests..."
        pytest tests/test_equivalence_bva.py -v
        ;;
    selenium)
        echo "Running Selenium UI tests..."
        pytest tests/test_selenium_ui.py -v -m selenium
        ;;
    ui)
        echo "Running UI tests (alias for selenium)..."
        pytest tests/test_selenium_ui.py -v -m selenium
        ;;
    auth)
        echo "Running authentication tests..."
        pytest tests/test_auth.py -v
        ;;
    security)
        echo "Running security tests..."
        pytest tests/test_security.py -v -m security
        ;;
    performance)
        echo "Running performance tests..."
        pytest tests/test_performance.py -v -m performance
        ;;
    load)
        echo "Running load tests..."
        pytest tests/test_load_stress.py -v -m load
        ;;
    stress)
        echo "Running stress tests..."
        pytest tests/test_load_stress.py -v -m stress
        ;;
    acceptance)
        echo "Running acceptance tests..."
        pytest tests/test_acceptance.py -v -m acceptance
        ;;
    coverage)
        echo "Generating detailed coverage report..."
        echo "Installing pytest-cov if needed..."
        pip install pytest-cov >/dev/null 2>&1 || true
        pytest --cov=core --cov=api --cov-report=html --cov-report=term-missing
        echo "Coverage report generated in htmlcov/index.html"
        ;;
    quick)
        echo "Running quick tests (no slow tests)..."
        pytest -m "not slow" -v
        ;;
    *)
        echo "Usage: ./run_tests.sh [option] [specific_test]"
        echo ""
        echo "Options:"
        echo "  all           - Run all tests with coverage (default)"
        echo "  unit          - Run only unit tests"
        echo "  integration   - Run API integration tests"
        echo "  redis         - Run all redis module tests"
        echo "  roster-utils  - Run roster_utils module tests"
        echo "  equivalence   - Run equivalence partitioning and BVA tests"
        echo "  selenium      - Run Selenium UI tests"
        echo "  ui            - Run UI tests (alias for selenium)"
        echo "  auth          - Run authentication tests"
        echo "  security      - Run security tests (JWT, RBAC, auth bypass)"
        echo "  performance   - Run performance tests (caching, response times)"
        echo "  load          - Run load tests (concurrent users, pooling)"
        echo "  stress        - Run stress tests (high load, resource limits)"
        echo "  acceptance    - Run acceptance tests (end-to-end workflows)"
        echo "  build-key     - Run build_cache_key tests only"
        echo "  set-cache     - Run set_cache tests only"
        echo "  get-cache     - Run get_cache tests only"
        echo "  delete-cache  - Run delete_cache tests only"
        echo "  clear-cache   - Run clear_cache tests only"
        echo "  exists        - Run exists tests only"
        echo "  coverage      - Generate detailed HTML coverage report"
        echo "  quick         - Run quick tests (skip slow tests)"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh redis                                          # All redis tests"
        echo "  ./run_tests.sh roster-utils                                   # All roster_utils tests"
        echo "  ./run_tests.sh selenium                                       # Selenium UI tests"
        echo "  ./run_tests.sh auth                                           # Authentication tests"
        echo "  ./run_tests.sh security                                       # Security tests"
        echo "  ./run_tests.sh performance                                    # Performance tests"
        echo "  ./run_tests.sh load                                           # Load tests"
        echo "  ./run_tests.sh stress                                         # Stress tests"
        echo "  ./run_tests.sh acceptance                                     # Acceptance tests"
        echo "  ./run_tests.sh integration                                    # All API integration tests"
        echo "  ./run_tests.sh equivalence                                    # Equivalence & BVA tests"
        echo "  ./run_tests.sh build-key                                      # All build_cache_key tests"
        echo "  ./run_tests.sh redis TestBuildCacheKey                        # Specific test class"
        echo "  ./run_tests.sh redis TestBuildCacheKey::test_with_single_param # Specific test"
        exit 1
        ;;
esac

echo ""
echo "Tests completed"
