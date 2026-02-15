.PHONY: test test-unit test-cov test-quick install install-dev clean help

help:
	@echo "Available commands:"
	@echo "  make install      - Install package and dependencies"
	@echo "  make install-dev  - Install package with dev dependencies"
	@echo "  make test         - Run all tests with coverage"
	@echo "  make test-unit    - Run unit tests only (fast)"
	@echo "  make test-quick   - Run tests without coverage (fast)"
	@echo "  make test-cov     - Run tests and open coverage report"
	@echo "  make clean        - Clean build artifacts and cache"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	python scripts/run_tests.py

test-unit:
	python -m unittest discover -s tests -p "test_*.py" -v

test-quick:
	python -m pytest tests/ -v

test-cov:
	python scripts/run_tests.py
	@echo "Opening coverage report..."
	@if command -v xdg-open > /dev/null; then \
		xdg-open htmlcov/index.html; \
	elif command -v open > /dev/null; then \
		open htmlcov/index.html; \
	else \
		echo "Open htmlcov/index.html in your browser"; \
	fi

update-badges:
	python scripts/update_badges.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

