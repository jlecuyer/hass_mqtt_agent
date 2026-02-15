# Test Coverage

## Overview
This directory contains unit tests and integration tests for the HASS MQTT Agent.

## Running Tests

### Quick Test (unittest only)
```bash
python scripts/run_tests.py --unit-only
```

### Full Test Suite with Coverage
```bash
python scripts/run_tests.py
```

Or directly with pytest:
```bash
pytest tests/ -v --cov=src/hass_mqtt_agent --cov-report=term-missing
```

### Run Specific Test File
```bash
python -m pytest tests/test_pc_status_monitor.py -v
```

### Run Specific Test
```bash
python -m pytest tests/test_pc_status_monitor.py::TestPCStatusMonitor::test_is_game_running_true -v
```

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_pc_status_monitor.py` - Tests for PCStatusMonitor class
- `test_hass_mqtt_agent.py` - Tests for HASSMQTTAgent class
- `test_setup_config.py` - Tests for configuration setup scripts
- `test_integration.py` - Integration tests for full workflows
- `test_build.py` - Tests for build scripts

## Coverage Goals

We aim for:
- **80%+** overall code coverage
- **90%+** coverage for core modules (PCStatusMonitor, HASSMQTTAgent)
- **100%** coverage for critical paths (commands, state publishing)

## Writing Tests

### Example Unit Test
```python
def test_example(self):
    """Test description"""
    # Arrange
    monitor = PCStatusMonitor([])
    
    # Act
    result = monitor.is_game_running()
    
    # Assert
    self.assertFalse(result)
```

### Example Mock Test
```python
@patch('psutil.cpu_percent')
def test_with_mock(self, mock_cpu):
    """Test with mocked dependency"""
    mock_cpu.return_value = 50.0
    
    monitor = PCStatusMonitor([])
    info = monitor.get_system_info()
    
    self.assertEqual(info['cpu_percent'], 50.0)
```

## Fixtures (pytest)

Use fixtures from `conftest.py`:
```python
def test_with_config(config_file):
    """Test using config file fixture"""
    agent = HASSMQTTAgent(config_file)
    assert agent.config is not None
```

## Continuous Integration

Tests are automatically run on every push via GitHub Actions.
See `.github/workflows/build.yml` for CI configuration.

