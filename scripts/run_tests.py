#!/usr/bin/env python3
"""
Test runner script for HASS MQTT Agent
Runs all unit tests and generates coverage report
"""

import sys
import subprocess
import os
from pathlib import Path


def run_tests():
    """Run all tests with coverage"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("=" * 70)
    print("Running HASS MQTT Agent Test Suite")
    print("=" * 70)
    print()

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--cov=src/hass_mqtt_agent",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml"
    ]

    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    print()
    print("=" * 70)

    if result.returncode == 0:
        print("✅ All tests passed!")
        print()
        print("Coverage report generated:")
        print("  - Terminal: (above)")
        print("  - HTML: htmlcov/index.html")
        print("  - XML: coverage.xml")
    else:
        print("❌ Tests failed!")
        sys.exit(1)

    print("=" * 70)

    return result.returncode


def run_unit_tests_only():
    """Run only unit tests (faster)"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("Running unit tests only...")

    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s", "tests",
        "-p", "test_*.py",
        "-v"
    ]

    result = subprocess.run(cmd)
    return result.returncode


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--unit-only':
        exit_code = run_unit_tests_only()
    else:
        exit_code = run_tests()

    sys.exit(exit_code)

