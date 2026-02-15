# 🎉 Project Update: Cross-Platform + Setup Wizards

## What's New in This Version

This update transforms the HASS MQTT Agent into a professional, cross-platform application with easy setup and installation tools.

### ✨ Major Features Added

1. **🖥️ Full Cross-Platform Support**
   - Windows (7/10/11)
   - Linux (systemd-based distributions)
   - macOS (partial support)

2. **🧙 Interactive Setup Wizards**
   - Beautiful GUI wizard (tkinter)
   - Terminal/CLI wizard for headless systems
   - Auto-launches on first run if no config found

3. **📁 Organized Scripts Directory**
   - All setup and installation scripts in one place
   - Platform-specific installers
   - Comprehensive documentation

4. **🔧 Service Installation**
   - Windows Service installer (PowerShell)
   - Linux systemd installer (Python)
   - Auto-start on boot configuration

---

## 📂 New Project Structure

```
hass_mqtt_agent/
├── main.py                    # Cross-platform agent
├── config.yaml                # Your configuration
├── config.yaml.example        # Template with platform examples
│
├── scripts/                   # NEW! All scripts organized here
│   ├── README.md              # Scripts documentation
│   ├── setup_config.py        # Terminal wizard
│   ├── setup_config_gui.py    # GUI wizard
│   ├── install_windows.ps1    # Windows installer
│   └── install_systemd.py     # Linux installer
│
├── Documentation/
│   ├── README.md              # Main documentation
│   ├── QUICKSTART.md          # Quick start guide
│   ├── CROSS_PLATFORM.md      # NEW! Platform guide
│   ├── TROUBLESHOOTING.md     # Troubleshooting
│   ├── ARCHITECTURE.md        # Architecture details
│   ├── BUILD.md               # Build instructions
│   └── CHANGELOG.md           # Version history
│
└── Other files...
```

---

## 🚀 Quick Start (New User Experience)

### First Run - Automatic Setup

Simply run the agent:

```bash
python main.py
```

If no `config.yaml` exists, you'll see:

```
Home Assistant MQTT Agent
==================================================

⚠️  Configuration file not found!

You have the following options:
  1. Run the GUI setup wizard (recommended)
  2. Run the terminal setup wizard
  3. Manually copy config.yaml.example to config.yaml
  4. Exit and configure later

Select option (1-4): 
```

Choose option **1** for the beautiful GUI wizard!

---

## 🖥️ Platform-Specific Quick Starts

### Windows

```powershell
# 1. Install Python 3.10+ from python.org

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run setup wizard
python scripts/setup_config_gui.py

# 4. Test the agent
python main.py

# 5. Install as Windows Service (as Administrator)
.\scripts\install_windows.ps1
```

### Linux

```bash
# 1. Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip python3-tk

# 2. Install Python packages
pip3 install -r requirements.txt

# 3. Run setup wizard
python3 scripts/setup_config_gui.py
# OR for terminal-only systems:
python3 scripts/setup_config.py

# 4. Test the agent
python3 main.py

# 5. Install as systemd service
sudo python3 scripts/install_systemd.py
```

---

## 🎨 Setup Wizard Features

### GUI Wizard (`setup_config_gui.py`)

A beautiful 7-step wizard:

1. **Welcome** - Introduction
2. **MQTT Broker** - Configure connection
3. **Home Assistant** - Device settings
4. **Agent Config** - Update intervals
5. **Game Folders** - Browse and select folders
6. **Custom Commands** - Define commands (optional)
7. **Summary** - Review and save

**Features:**
- Visual interface
- Platform-aware defaults
- Folder browser
- Input validation
- Configuration backup
- Summary preview

### Terminal Wizard (`setup_config.py`)

Full-featured CLI wizard for SSH/headless systems:

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        Home Assistant MQTT Agent - Setup Wizard           ║
║                                                            ║
║    This wizard will help you create your config.yaml      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

**Features:**
- Interactive prompts
- Smart defaults
- Platform detection
- Works over SSH
- Validation
- Progress feedback

---

## 🔧 Cross-Platform Features

### Power Management

| Command | Windows | Linux | macOS |
|---------|---------|-------|-------|
| Shutdown | ✅ `shutdown /s` | ✅ `systemctl poweroff` | ✅ `shutdown -h` |
| Reboot | ✅ `shutdown /r` | ✅ `systemctl reboot` | ✅ `shutdown -r` |
| Sleep | ✅ `rundll32` | ✅ `systemctl suspend` | ✅ `pmset sleepnow` |

Automatically detects your platform and uses the correct command!

### Game Detection

**Windows:**
- Scans for `.exe` files
- Example: `C:\Program Files (x86)\Steam\steamapps\common`

**Linux:**
- Scans for executable files
- Example: `~/.steam/steam/steamapps/common`

**Both:**
- Automatic scanning at startup
- Detects when games run
- Validates process paths

### Service Integration

**Windows Service:**
- Install: `python main.py install`
- Start: `python main.py start`
- Stop: `python main.py stop`
- Managed via `services.msc`

**Linux systemd:**
- Install: `sudo python3 scripts/install_systemd.py`
- Start: `sudo systemctl start hass-mqtt-agent`
- Stop: `sudo systemctl stop hass-mqtt-agent`
- Logs: `sudo journalctl -u hass-mqtt-agent -f`

---

## 📚 Documentation

### For Users

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[CROSS_PLATFORM.md](CROSS_PLATFORM.md)** - Platform-specific guide
- **[scripts/README.md](scripts/README.md)** - Scripts documentation
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues

### For Developers

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
- **[BUILD.md](BUILD.md)** - Building wheels
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute (if exists)

---

## 🎯 Key Benefits

### For End Users

1. **Easy Setup** - GUI wizard walks you through configuration
2. **Cross-Platform** - Works on Windows and Linux
3. **Auto-Detection** - Platform-aware defaults
4. **Professional** - Service/systemd integration
5. **No Manual Config** - Everything via wizards

### For System Administrators

1. **Scriptable** - Terminal wizard for automation
2. **Systemd Support** - Standard Linux service
3. **Logging** - Proper log files and journalctl integration
4. **Permissions** - Documented sudo requirements
5. **Uninstall** - Clean removal instructions

### For Developers

1. **Cross-Platform Code** - Examples and patterns
2. **Organized** - Scripts separated from core
3. **Documented** - Comprehensive guides
4. **Testable** - Platform detection transparent
5. **Extensible** - Easy to add new platforms

---

## 🔄 Migration from Previous Version

### If you have existing `config.yaml`

**No changes needed!** Your configuration is fully compatible.

### If you used `install.ps1` before

The file has moved to `scripts/install_windows.ps1`. Update any documentation or automation:

```powershell
# Old
.\install.ps1

# New
.\scripts\install_windows.ps1
```

---

## 🆕 What's Different

### Before This Update

```bash
# Manual configuration required
cp config.yaml.example config.yaml
nano config.yaml  # Edit manually

# Windows-only
# Limited documentation
# Single install script in root
```

### After This Update

```bash
# Interactive setup
python scripts/setup_config_gui.py  # Beautiful wizard!

# Cross-platform
# Comprehensive documentation
# Organized scripts directory
# Platform-specific installers
```

---

## 📊 Statistics

- **New Files:** 5 (4 scripts + 1 doc)
- **Modified Files:** 6
- **New Lines of Code:** ~1,800
- **Platforms Supported:** 2 (Windows, Linux) + 1 partial (macOS)
- **Setup Options:** 3 (GUI, Terminal, Manual)
- **Documentation Pages:** 4 new/updated

---

## 🎓 Learn More

### Explore the Scripts

```bash
cd scripts/
ls -la

# Read the documentation
cat README.md

# Try the wizards
python3 setup_config.py       # Terminal
python3 setup_config_gui.py   # GUI
```

### Platform Guides

- **Windows users:** See [CROSS_PLATFORM.md - Windows Section](CROSS_PLATFORM.md#windows)
- **Linux users:** See [CROSS_PLATFORM.md - Linux Section](CROSS_PLATFORM.md#linux)

### Troubleshooting

- GUI won't start on Linux? Install tkinter: `sudo apt install python3-tk`
- Permission errors? See [CROSS_PLATFORM.md - Permissions](CROSS_PLATFORM.md#permissions-on-linux)
- Service won't install? Check the installer output for specific errors

---

## 🤝 Contributing

Want to help improve the agent?

1. Add support for more platforms (BSD, macOS, etc.)
2. Improve the setup wizards
3. Add more custom command examples
4. Write tests
5. Improve documentation

See the repository for contribution guidelines!

---

## 📝 License

MIT License - Free to use, modify, and distribute!

---

## 🎊 Thank You!

This update makes the HASS MQTT Agent accessible to more users across more platforms. Whether you're on Windows or Linux, desktop or headless server, the setup wizards make configuration a breeze!

**Enjoy controlling your PC from Home Assistant!** 🏠🎮

---

**Questions? Issues? Suggestions?**

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [scripts/README.md](scripts/README.md)
- Read [CROSS_PLATFORM.md](CROSS_PLATFORM.md)
- Open an issue on GitHub

**Happy automating!** 🚀

