# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-02-14

### Added

#### Game Detection Improvements
- **Folder-based game detection**: Instead of manually listing process names, the agent now scans configured game installation folders
- Automatically discovers all `.exe` files in configured game folders at startup
- Validates running processes against both executable name and installation path
- Supports Windows environment variables in folder paths (e.g., `%PROGRAMFILES(X86)%`)
- New `rescan_game_folders()` method to refresh game list without restarting service
- Detailed logging of game folder scanning process

#### Build and Distribution
- **GitHub Actions workflow** for automated wheel building
- Automatic builds on version tags (creates GitHub Releases)
- Manual workflow trigger support
- Build validation on pull requests
- Proper `pyproject.toml` configuration for wheel building
- `MANIFEST.in` for including documentation files in distribution
- `BUILD.md` documentation for building wheels locally
- MIT License file

#### Documentation
- Complete project documentation suite:
  - `README.md` - Comprehensive usage guide
  - `QUICKSTART.md` - 5-minute setup guide
  - `TROUBLESHOOTING.md` - Common issues and solutions
  - `ARCHITECTURE.md` - System architecture diagrams
  - `PROJECT_SUMMARY.md` - Project overview
  - `BUILD.md` - Wheel building instructions
- `homeassistant_examples.yaml` - Ready-to-use Home Assistant configurations
- PowerShell installation script (`install.ps1`)

### Changed

#### Configuration
- **Breaking**: `game_processes` renamed to `game_folders` in `config.yaml`
- Configuration now expects folder paths instead of process names
- Updated all config examples to use folder-based detection

#### Game Detection Logic
- Replaced pattern-matching process detection with executable catalog
- Improved performance by building executable set once at startup
- More accurate detection by validating process path location
- Better logging for detected games

### Configuration Migration

If upgrading from a previous version, update your `config.yaml`:

**Old format:**
```yaml
agent:
  game_processes:
    - "steam.exe"
    - "GTA5.exe"
    - "csgo.exe"
```

**New format:**
```yaml
agent:
  game_folders:
    - "C:\\Program Files (x86)\\Steam\\steamapps\\common"
    - "D:\\SteamLibrary\\steamapps\\common"
    - "C:\\Program Files\\Epic Games"
```

### Technical Details

#### Code Changes
- `PCStatusMonitor.__init__()` now accepts `game_folders` parameter
- New `_scan_game_folders()` method for recursive folder scanning
- Enhanced `is_game_running()` with path validation
- Added `game_executables` set to store discovered executables
- Support for `os.path.expandvars()` for environment variable expansion

#### Build System
- Uses `setuptools.build_meta` build backend
- Proper package metadata in `pyproject.toml`
- Platform-specific dependencies (pywin32 only on Windows)
- Includes all documentation in wheel distribution

### Files Changed
- `main.py` - Updated game detection logic
- `config.yaml` - New folder-based configuration
- `config.yaml.example` - Updated with folder examples
- `pyproject.toml` - Complete build configuration
- `README.md` - Updated documentation
- `QUICKSTART.md` - Updated setup instructions

### New Files
- `.github/workflows/build.yml` - CI/CD workflow
- `MANIFEST.in` - Distribution file manifest
- `LICENSE` - MIT License
- `BUILD.md` - Build instructions
- `CHANGELOG.md` - This file

## Future Enhancements

Planned features for future releases:

### Game Detection
- [ ] Periodic rescanning of game folders (auto-detect new installations)
- [ ] Game-specific status (which game is running)
- [ ] Play time tracking
- [ ] Game launch/close event notifications
- [ ] Configurable scan depth (limit folder recursion)
- [ ] Exclude patterns (ignore certain folders/files)

### Control Features
- [ ] Hibernate command
- [ ] Lock workstation command
- [ ] Kill process command
- [ ] Volume control
- [ ] Display on/off
- [ ] Scheduled tasks

### Monitoring
- [ ] Disk usage monitoring
- [ ] Network activity monitoring
- [ ] GPU usage monitoring (if available)
- [ ] Temperature sensors
- [ ] Active window detection

### Integration
- [ ] Multiple PC support (one Home Assistant, multiple PCs)
- [ ] WebSocket support (alternative to MQTT)
- [ ] REST API endpoint
- [ ] Discord/Telegram notifications

### Service Improvements
- [ ] Graceful command cancellation
- [ ] Command queue system
- [ ] Service health checks
- [ ] Automatic service recovery
- [ ] Configuration hot-reload (no restart needed)

### Developer Experience
- [ ] Unit tests
- [ ] Integration tests
- [ ] Pre-commit hooks
- [ ] Code formatting (black/ruff)
- [ ] Type hints validation (mypy)

## Version History

- **0.1.0** (2026-02-14) - Initial release with folder-based game detection and build workflow

---

## How to Contribute

See the repository for contribution guidelines. All contributions are welcome!

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub with:
- Your Windows version
- Python version
- Agent version
- Config file (with sensitive data removed)
- Log file output
- Steps to reproduce

## Security

For security issues, please do not open a public issue. Contact the maintainers directly.

