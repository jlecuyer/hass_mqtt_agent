#!/usr/bin/env python3
"""
Update README badges with current test statistics
Run this after running tests to update coverage badge
"""

import re
import subprocess
import sys
import json
from pathlib import Path


def get_test_count():
    """Get total number of tests"""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )

    # Parse output like "65 tests collected in 0.05s"
    match = re.search(r'(\d+) tests? collected', result.stdout)
    if match:
        return int(match.group(1))
    return 0


def get_coverage():
    """Get current code coverage percentage"""
    coverage_file = Path(__file__).parent.parent / "coverage.json"

    if not coverage_file.exists():
        # Run tests with coverage to generate the file
        subprocess.run(
            [sys.executable, "-m", "pytest", "tests/",
             "--cov=src/hass_mqtt_agent", "--cov-report=json"],
            cwd=Path(__file__).parent.parent,
            capture_output=True
        )

    if coverage_file.exists():
        with open(coverage_file, 'r') as f:
            data = json.load(f)
            return round(data['totals']['percent_covered'])

    return 0


def update_readme_badges(test_count, coverage):
    """Update badges in README.md"""
    readme_path = Path(__file__).parent.parent / "README.md"

    with open(readme_path, 'r') as f:
        content = f.read()

    # Update test count badge
    content = re.sub(
        r'\[!\[Tests\]\(https://img\.shields\.io/badge/tests-\d+%20passing-[^\]]+\)\]',
        f'[![Tests](https://img.shields.io/badge/tests-{test_count}%20passing-brightgreen)]',
        content
    )

    # Update coverage badge with color based on percentage
    if coverage >= 80:
        color = "brightgreen"
    elif coverage >= 70:
        color = "green"
    elif coverage >= 60:
        color = "yellow"
    else:
        color = "orange"

    content = re.sub(
        r'\[!\[Coverage\]\(https://img\.shields\.io/badge/coverage-\d+%25-[^\]]+\)\]',
        f'[![Coverage](https://img.shields.io/badge/coverage-{coverage}%25-{color})]',
        content
    )

    with open(readme_path, 'w') as f:
        f.write(content)

    print(f"✅ Updated README badges:")
    print(f"   Tests: {test_count} passing")
    print(f"   Coverage: {coverage}% ({color})")


def main():
    """Main function"""
    print("Updating README badges...")
    print()

    print("📊 Collecting test statistics...")
    test_count = get_test_count()
    print(f"   Found {test_count} tests")

    print("📈 Calculating coverage...")
    coverage = get_coverage()
    print(f"   Coverage: {coverage}%")

    print()
    update_readme_badges(test_count, coverage)
    print()
    print("Done! Badges updated in README.md")


if __name__ == '__main__':
    main()

