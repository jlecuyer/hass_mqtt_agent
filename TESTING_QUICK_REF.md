# HASS MQTT Agent - Testing Quick Reference

## 🚀 Quick Commands

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
make test
# or
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src/hass_mqtt_agent --cov-report=html

# Run specific test file
pytest tests/test_pc_status_monitor.py -v

# Run specific test
pytest tests/test_pc_status_monitor.py::TestPCStatusMonitor::test_is_game_running_true -v

# Skip slow tests
pytest tests/ -m "not slow"

# View coverage report
make test-cov
```

## 📊 Test Statistics

- **Total Tests**: 65
- **Coverage**: 59%
- **Status**: ✅ All Passing

## 📁 Test Structure

```
tests/
├── test_pc_status_monitor.py  (11 tests) - System monitoring
├── test_hass_mqtt_agent.py    (17 tests) - MQTT agent core
├── test_integration.py        (4 tests)  - End-to-end tests
├── test_setup_config.py       (11 tests) - Config wizard
├── test_pytest_features.py    (22 tests) - Advanced tests
└── test_build.py              (4 tests)  - Build system
```

## 📚 Documentation

- **tests/README.md** - Quick test guide
- **docs/TESTING.md** - Complete testing documentation
- **TEST_IMPLEMENTATION_SUMMARY.md** - Implementation details

## 🔍 What's Covered

✅ Configuration loading & validation  
✅ MQTT connection & authentication  
✅ Command execution (shutdown/reboot/sleep/custom)  
✅ State publishing & HA discovery  
✅ Game detection & system monitoring  
✅ Error handling & edge cases  
✅ Platform-specific behavior (Windows/Linux)

## 💡 Tips

- Use `--tb=short` for shorter tracebacks
- Use `-v` for verbose output
- Use `-x` to stop on first failure
- Use `-k pattern` to run tests matching pattern
- Use `--lf` to rerun last failed tests
- Use `--cov-report=html` for visual coverage report

## 🎯 Coverage Goals

| Level | Status |
|-------|--------|
| 80%+  | ✅ Excellent |
| 70-79%| ✓ Good |
| 60-69%| ⚠ Fair (current) |
| <60%  | ❌ Needs improvement |

Current: **59%** → Target: **80%+**

