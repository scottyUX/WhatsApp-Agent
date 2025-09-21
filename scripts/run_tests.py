#!/usr/bin/env python3
"""
Test runner script for WhatsApp Agent
Runs different test suites based on command line arguments
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def run_unit_tests():
    """Run unit tests"""
    return run_command(
        "python -m pytest tests/test_unit.py -v --tb=short",
        "Unit Tests"
    )

def run_integration_tests():
    """Run integration tests"""
    return run_command(
        "python -m pytest tests/test_integration.py -v --tb=short",
        "Integration Tests"
    )

def run_e2e_tests():
    """Run end-to-end tests"""
    return run_command(
        "python -m pytest tests/test_e2e.py -v --tb=short",
        "End-to-End Tests"
    )

def run_api_tests():
    """Run API tests"""
    return run_command(
        "python -m pytest tests/test_api.py -v --tb=short",
        "API Tests"
    )

def run_all_tests():
    """Run all tests"""
    return run_command(
        "python -m pytest tests/ -v --tb=short",
        "All Tests"
    )

def run_fast_tests():
    """Run fast tests only (unit + integration)"""
    return run_command(
        "python -m pytest tests/test_unit.py tests/test_integration.py -v --tb=short",
        "Fast Tests (Unit + Integration)"
    )

def run_slow_tests():
    """Run slow tests (e2e + api)"""
    return run_command(
        "python -m pytest tests/test_e2e.py tests/test_api.py -v --tb=short",
        "Slow Tests (E2E + API)"
    )

def run_coverage():
    """Run tests with coverage report"""
    return run_command(
        "python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing",
        "Tests with Coverage"
    )

def run_linting():
    """Run code linting"""
    return run_command(
        "python -m black --check app/ tests/",
        "Code Linting (Black)"
    )

def run_type_checking():
    """Run type checking"""
    return run_command(
        "python -m mypy app/ --ignore-missing-imports",
        "Type Checking (MyPy)"
    )

def run_security_scan():
    """Run security scanning"""
    return run_command(
        "python -m bandit -r app/ -f json -o security-report.json",
        "Security Scan (Bandit)"
    )

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="WhatsApp Agent Test Runner")
    parser.add_argument(
        "test_type",
        choices=[
            "unit", "integration", "e2e", "api", "all", "fast", "slow",
            "coverage", "lint", "type-check", "security", "pre-deploy"
        ],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    print("🚀 WhatsApp Agent Test Runner")
    print("=" * 60)
    print(f"Test Type: {args.test_type}")
    print(f"Project Root: {project_root}")
    print("=" * 60)
    
    success = True
    
    if args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "e2e":
        success = run_e2e_tests()
    elif args.test_type == "api":
        success = run_api_tests()
    elif args.test_type == "all":
        success = run_all_tests()
    elif args.test_type == "fast":
        success = run_fast_tests()
    elif args.test_type == "slow":
        success = run_slow_tests()
    elif args.test_type == "coverage":
        success = run_coverage()
    elif args.test_type == "lint":
        success = run_linting()
    elif args.test_type == "type-check":
        success = run_type_checking()
    elif args.test_type == "security":
        success = run_security_scan()
    elif args.test_type == "pre-deploy":
        print("Running Pre-Deployment Test Suite...")
        success = (
            run_linting() and
            run_unit_tests() and
            run_integration_tests() and
            run_api_tests() and
            run_coverage()
        )
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

