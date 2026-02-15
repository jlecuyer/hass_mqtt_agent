#!/usr/bin/env python3
"""
Generate test coverage summary report
"""

import subprocess
import sys
import json
from pathlib import Path


def generate_summary():
    """Generate and display test summary"""
    project_root = Path(__file__).parent.parent

    print("=" * 80)
    print("HASS MQTT Agent - Test Coverage Summary")
    print("=" * 80)
    print()

    # Run tests and capture output
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v",
         "--cov=src/hass_mqtt_agent", "--cov-report=json", "--cov-report=term"],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    # Read coverage JSON for detailed stats
    coverage_file = project_root / "coverage.json"
    if coverage_file.exists():
        with open(coverage_file, 'r') as f:
            coverage_data = json.load(f)

        total_coverage = coverage_data['totals']['percent_covered']

        print()
        print("=" * 80)
        print(f"Overall Coverage: {total_coverage:.2f}%")

        # Coverage targets
        if total_coverage >= 80:
            status = "✅ EXCELLENT"
        elif total_coverage >= 70:
            status = "✓ GOOD"
        elif total_coverage >= 60:
            status = "⚠ FAIR"
        else:
            status = "❌ NEEDS IMPROVEMENT"

        print(f"Status: {status}")
        print("=" * 80)
        print()

        # Detailed file coverage
        print("File-by-File Coverage:")
        print("-" * 80)
        files = coverage_data.get('files', {})
        for filepath, data in sorted(files.items()):
            filename = Path(filepath).name
            coverage_pct = data['summary']['percent_covered']
            bars = int(coverage_pct / 2)
            bar = "█" * bars + "░" * (50 - bars)
            print(f"  {filename:40s} {bar} {coverage_pct:6.2f}%")
        print()

        return result.returncode
    else:
        print("⚠ Coverage JSON not generated")
        return result.returncode


if __name__ == '__main__':
    exit_code = generate_summary()
    sys.exit(exit_code)

