#!/bin/bash
# Quick test runner for CI/CD or local development

set -e

echo "================================"
echo "HASS MQTT Agent - Quick Test"
echo "================================"
echo ""

# Check if pytest is installed
if ! python -m pytest --version &> /dev/null; then
    echo "⚠️  pytest not installed. Installing test dependencies..."
    python -m pip install pytest pytest-cov pytest-mock -q
fi

# Run tests
echo "Running tests..."
python -m pytest tests/ -v --tb=short

# Show summary
echo ""
echo "================================"
echo "✅ All tests passed!"
echo "================================"

