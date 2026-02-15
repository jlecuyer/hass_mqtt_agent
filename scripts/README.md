# Scripts Directory

This directory contains various scripts for setting up, installing, and managing the HASS MQTT Agent.

## Setup Scripts

### GUI Configuration Wizard (Recommended)
**File:** `setup_config_gui.py`

Interactive GUI wizard for creating `config.yaml`.

**Requirements:**
- Python with tkinter support
- On Linux: `sudo apt-get install python3-tk`

**Usage:**
```bash
python scripts/setup_config_gui.py
```

**Features:**
- Visual step-by-step configuration
- Platform-aware defaults
- Folder browser for game directories
- Configuration validation
- Summary review before saving

---

### Terminal Configuration Wizard
**File:** `setup_config.py`

Text-based interactive configuration wizard for headless systems or users who prefer terminal.

**Requirements:**
- Python 3.10+
- pyyaml

**Usage:**
```bash
python scripts/setup_config.py
```

**Features:**
- Works in SSH sessions
- No GUI required
- Same configuration options as GUI
- Automatic platform detection
- Suggested default values

---

## Installation Scripts

### Windows Service Installer
**File:** `install_windows.ps1`

PowerShell script to install HASS MQTT Agent as a Windows Service.

**Requirements:**
- Windows 10/11
- PowerShell
- Administrator privileges
- Python with pywin32 installed

**Usage:**
```powershell
# Run as Administrator
.\scripts\install_windows.ps1
```

**What it does:**
1. Checks Python installation
2. Installs Python dependencies
3. Validates configuration
4. Tests agent in console mode (optional)
5. Installs as Windows service
6. Starts the service

**Service Management:**
```powershell
python main.py start    # Start service
python main.py stop     # Stop service
python main.py restart  # Restart service
python main.py remove   # Uninstall service
```

---

### Linux Systemd Service Installer
**File:** `install_systemd.py`

Python script to install HASS MQTT Agent as a systemd service on Linux.

**Requirements:**
- Linux with systemd
- Python 3.10+
- sudo/root access

**Usage:**
```bash
sudo python scripts/install_systemd.py
```

**What it does:**
1. Checks for config.yaml
2. Creates systemd service file
3. Enables service for auto-start
4. Starts the service
5. Shows status

**Service Management:**
```bash
sudo systemctl start hass-mqtt-agent      # Start
sudo systemctl stop hass-mqtt-agent       # Stop
sudo systemctl restart hass-mqtt-agent    # Restart
sudo systemctl status hass-mqtt-agent     # Status
sudo journalctl -u hass-mqtt-agent -f     # View logs
```

**Uninstall:**
```bash
sudo systemctl stop hass-mqtt-agent
sudo systemctl disable hass-mqtt-agent
sudo rm /etc/systemd/system/hass-mqtt-agent.service
sudo systemctl daemon-reload
```

---

## Quick Start Guide

### First Time Setup

**Option 1: GUI (Recommended for desktop users)**
```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI setup wizard
python scripts/setup_config_gui.py

# Test the agent
python main.py
```

**Option 2: Terminal (For SSH/headless systems)**
```bash
# Install dependencies
pip install -r requirements.txt

# Run terminal setup wizard
python scripts/setup_config.py

# Test the agent
python main.py
```

**Option 3: Manual**
```bash
# Copy example config
cp config.yaml.example config.yaml

# Edit with your settings
nano config.yaml  # or vim, or any editor

# Test the agent
python main.py
```

---

### Install as Service

**Windows:**
```powershell
# Run as Administrator
.\scripts\install_windows.ps1
```

**Linux:**
```bash
sudo python scripts/install_systemd.py
```

---

## Platform Support

| Script | Windows | Linux | macOS |
|--------|---------|-------|-------|
| `setup_config_gui.py` | ✅ | ✅* | ✅ |
| `setup_config.py` | ✅ | ✅ | ✅ |
| `install_windows.ps1` | ✅ | ❌ | ❌ |
| `install_systemd.py` | ❌ | ✅ | ❌** |

\* Requires `python3-tk` package  
\** macOS uses launchd instead of systemd

---

## Troubleshooting

### GUI Won't Start (Linux)
```bash
# Install tkinter
sudo apt-get update
sudo apt-get install python3-tk

# Verify
python3 -c "import tkinter"
```

### Permission Denied on Scripts
```bash
# Make scripts executable
chmod +x scripts/*.py
```

### Service Won't Install (Windows)
- Ensure running PowerShell as Administrator
- Check pywin32 is installed: `pip install pywin32`
- Run post-install: `python Scripts/pywin32_postinstall.py -install`

### Service Won't Install (Linux)
- Use sudo: `sudo python scripts/install_systemd.py`
- Check systemd is available: `systemctl --version`
- Ensure config.yaml exists

### Configuration Not Saved
- Check write permissions in directory
- Ensure disk space available
- Check for YAML syntax errors

---

## Development Scripts

For developers working on the project:

### Run Tests (future)
```bash
# Will be added
python scripts/run_tests.py
```

### Build Package
```bash
# Build wheel
python -m build

# Install locally
pip install dist/hass_mqtt_agent-*.whl
```

### Lint Code (future)
```bash
# Will be added
python scripts/lint.py
```

---

## Script Locations

All scripts are in the `scripts/` directory:

```
scripts/
├── README.md                 # This file
├── setup_config.py          # Terminal setup wizard
├── setup_config_gui.py      # GUI setup wizard
├── install_windows.ps1      # Windows service installer
└── install_systemd.py       # Linux systemd installer
```

---

## Getting Help

If you encounter issues:

1. Check the main [README.md](../README.md)
2. Review [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
3. Check script output for error messages
4. Verify all dependencies are installed
5. Ensure you have proper permissions

---

## Contributing

To add new scripts:

1. Place them in the `scripts/` directory
2. Make them executable: `chmod +x script.py`
3. Add shebang: `#!/usr/bin/env python3`
4. Update this README
5. Add usage examples

---

**Note:** Always test configuration changes before deploying to production!

