# Testing Documentation

## Test Suite Overview

The HASS MQTT Agent has a comprehensive test suite with **65+ tests** covering:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Full workflow testing  
- **Mocked Tests**: External dependency isolation
- **Platform Tests**: Windows/Linux specific behavior

## Current Test Coverage

**Overall: ~59%** (Target: 80%+)

### Coverage by Module

| Module | Coverage | Status |
|--------|----------|--------|
| `__init__.py` | 100% | ✅ Excellent |
| `main.py` | 59% | ⚠ Needs improvement |

## Test Categories

### 1. PCStatusMonitor Tests (`test_pc_status_monitor.py`)

Tests for system monitoring functionality:

- ✅ Game folder scanning (Windows/Linux)
- ✅ Game process detection
- ✅ System information gathering (CPU, RAM)
- ✅ Folder rescanning
- ✅ Error handling

**11 tests** | All passing

### 2. HASSMQTTAgent Tests (`test_hass_mqtt_agent.py`)

Tests for MQTT agent core:

- ✅ Configuration loading
- ✅ MQTT connection setup
- ✅ Command execution (shutdown, reboot, sleep)
- ✅ Custom command handling
- ✅ State publishing
- ✅ Home Assistant discovery
- ✅ Platform-specific behavior

**17 tests** | All passing

### 3. Integration Tests (`test_integration.py`)

End-to-end workflow tests:

- ✅ Full agent lifecycle
- ✅ Command processing flow
- ✅ Status update loop
- ✅ Configuration validation

**4 tests** | All passing

### 4. Setup Config Tests (`test_setup_config.py`)

Tests for configuration wizard:

- ✅ User input handling
- ✅ Yes/No prompts
- ✅ Game folder selection
- ✅ Custom command setup

**11 tests** | All passing

### 5. Pytest Features (`test_pytest_features.py`)

Advanced pytest-style tests:

- ✅ Fixture usage
- ✅ Parametrized tests
- ✅ Error handling
- ✅ Performance tests

**22 tests** | All passing

## Running Tests

### Quick Commands

```bash
# All tests with coverage
make test

# Quick run (no coverage)
make test-quick

# Unit tests only
make test-unit

# Specific test file
pytest tests/test_pc_status_monitor.py -v

# Specific test
pytest tests/test_pc_status_monitor.py::TestPCStatusMonitor::test_is_game_running_true -v

# Skip slow tests
pytest tests/ -m "not slow" -v
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=src/hass_mqtt_agent --cov-report=html

# Open in browser
make test-cov

# Terminal report with missing lines
pytest tests/ --cov=src/hass_mqtt_agent --cov-report=term-missing
```

### Watch Mode (for development)

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw tests/ -- --cov=src/hass_mqtt_agent
```

## Test Fixtures

Reusable test fixtures in `conftest.py`:

- `temp_dir` - Temporary directory for test files
- `sample_config` - Sample configuration dictionary
- `config_file` - Temporary config.yaml file
- `game_folder` - Temporary folder with test game executables

### Using Fixtures

```python
def test_with_config(config_file):
    """Test using config file fixture"""
    agent = HASSMQTTAgent(config_file)
    assert agent.config is not None
```

## Writing New Tests

### Test Template

```python
import unittest
from unittest.mock import patch, MagicMock

class TestMyFeature(unittest.TestCase):
    """Test suite for MyFeature"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.test_data = {...}
    
    def tearDown(self):
        """Cleanup after tests"""
        pass
    
    def test_basic_functionality(self):
        """Test basic feature works"""
        # Arrange
        obj = MyClass()
        
        # Act
        result = obj.do_something()
        
        # Assert
        self.assertEqual(result, expected)
    
    @patch('module.external_dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependency"""
        mock_dep.return_value = "mocked"
        result = function_using_dependency()
        self.assertEqual(result, "mocked")
```

### Pytest Style Template

```python
import pytest

class TestMyFeature:
    """Pytest-style test suite"""
    
    def test_basic(self):
        """Basic test"""
        assert 1 + 1 == 2
    
    @pytest.mark.parametrize("input,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
    ])
    def test_parametrized(self, input, expected):
        """Parametrized test"""
        assert input * 2 == expected
    
    def test_with_fixture(self, config_file):
        """Test using fixture"""
        assert os.path.exists(config_file)
```

## Best Practices

### 1. Test Naming
- Use descriptive names: `test_game_detection_when_process_running`
- Follow pattern: `test_<what>_<when>_<expected>`

### 2. Arrange-Act-Assert Pattern
```python
def test_example(self):
    # Arrange - Setup test data
    monitor = PCStatusMonitor([])
    
    # Act - Execute the code
    result = monitor.is_game_running()
    
    # Assert - Verify results
    self.assertFalse(result)
```

### 3. Mock External Dependencies
```python
@patch('subprocess.run')
def test_shutdown(self, mock_run):
    """Mock subprocess to avoid actual shutdown"""
    agent._shutdown_pc()
    mock_run.assert_called_once()
```

### 4. Test Edge Cases
- Empty inputs
- None values
- Missing files
- Permission errors
- Network failures

### 5. Keep Tests Fast
- Mock slow operations
- Use small test data
- Mark slow tests with `@pytest.mark.slow`

## CI/CD Integration

Tests run automatically on:

- ✅ Every push to main/develop
- ✅ Every pull request
- ✅ Before releases

See `.github/workflows/build.yml` for CI configuration.

### GitHub Actions Workflow

1. Run tests on multiple Python versions (3.10, 3.11, 3.12)
2. Run tests on multiple platforms (Ubuntu, Windows)
3. Upload coverage to Codecov
4. Only build if tests pass

## Code Coverage Goals

| Coverage Level | Status |
|----------------|--------|
| 80%+ | ✅ Excellent |
| 70-79% | ✓ Good |
| 60-69% | ⚠ Fair |
| <60% | ❌ Needs improvement |

### Improving Coverage

Priority areas for additional tests:

1. Windows service functionality
2. Error handling paths
3. MQTT reconnection logic
4. Custom command validation
5. Configuration edge cases

## Troubleshooting Tests

### Tests Fail on Import
```bash
# Install package in development mode
pip install -e .
```

### Coverage Not Working
```bash
# Install coverage tools
pip install pytest-cov coverage
```

### Platform-Specific Tests Fail
```bash
# Tests may behave differently on Windows vs Linux
# Check test decorators: @patch('sys.platform', 'win32')
```

### Slow Test Suite
```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Run in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Docs](https://coverage.readthedocs.io/)

