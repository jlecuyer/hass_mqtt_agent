# Cross-Platform Support

The HASS MQTT Agent now supports both **Windows** and **Linux** platforms, with automatic platform detection and appropriate command execution.

## Platform Support Matrix

| Feature | Windows | Linux | Notes |
|---------|---------|-------|-------|
| MQTT Communication | ✅ | ✅ | Full support |
| Status Monitoring | ✅ | ✅ | CPU, Memory, Processes |
| Game Detection | ✅ | ✅ | Auto-scans game folders |
| Shutdown Command | ✅ | ✅ | Platform-specific |
| Reboot Command | ✅ | ✅ | Platform-specific |
| Sleep/Suspend | ✅ | ✅ | systemctl/pm-suspend on Linux |
| Custom Commands | ✅ | ✅ | Shell execution |
| Service Installation | ✅ | ✅ | Windows Service / systemd |
| GUI Setup Wizard | ✅ | ✅* | *Requires python3-tk on Linux |
| Terminal Setup | ✅ | ✅ | Full support |
| Auto-start on Boot | ✅ | ✅ | Via service |

## Platform-Specific Features

### Windows

#### Power Management
- Uses native Windows `shutdown` command
- Sleep via `rundll32.exe` and `powrprof.dll`
- 5-second delay for graceful shutdown/reboot

#### Service Management
- Windows Service integration via `pywin32`
- Managed through `services.msc` or command line
- Service commands:
  ```powershell
  python main.py install
  python main.py start
  python main.py stop
  python main.py restart
  python main.py remove
  ```

#### Game Detection
- Scans for `.exe` files
- Typical locations:
  - `C:\Program Files (x86)\Steam\steamapps\common`
  - `C:\Program Files\Epic Games`
  - `C:\XboxGames`

### Linux

#### Power Management
- Uses `systemctl` for modern systemd-based distros
- Falls back to traditional `shutdown` command
- Sleep/suspend via `systemctl suspend` or `pm-suspend`
- May require sudo/passwordless sudo for some commands

#### Service Management
- systemd service integration
- Service file: `/etc/systemd/system/hass-mqtt-agent.service`
- Service commands:
  ```bash
  sudo systemctl start hass-mqtt-agent
  sudo systemctl stop hass-mqtt-agent
  sudo systemctl restart hass-mqtt-agent
  sudo systemctl status hass-mqtt-agent
  sudo journalctl -u hass-mqtt-agent -f  # View logs
  ```

#### Game Detection
- Scans for executable files (with execute permission)
- Typical locations:
  - `~/.steam/steam/steamapps/common`
  - `~/.local/share/Steam/steamapps/common`
  - `~/Games`
  - Wine games: `~/.wine/drive_c/Program Files/...`

## Installation by Platform

### Windows Installation

1. **Install Python 3.10+**
   - Download from [python.org](https://www.python.org/)

2. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure (choose one)**
   - GUI: `python scripts/setup_config_gui.py`
   - Terminal: `python scripts/setup_config.py`
   - Manual: Copy `config.yaml.example` to `config.yaml`

4. **Install as Service**
   ```powershell
   # Run as Administrator
   .\scripts\install_windows.ps1
   ```

### Linux Installation

1. **Install Python 3.10+**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   
   # For GUI wizard (optional)
   sudo apt install python3-tk
   ```

2. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   # or in a virtual environment:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure (choose one)**
   - GUI: `python3 scripts/setup_config_gui.py`
   - Terminal: `python3 scripts/setup_config.py`
   - Manual: `cp config.yaml.example config.yaml && nano config.yaml`

4. **Install as systemd Service**
   ```bash
   sudo python3 scripts/install_systemd.py
   ```

## Configuration Differences

### Game Folders

**Windows:**
```yaml
agent:
  game_folders:
    - "C:\\Program Files (x86)\\Steam\\steamapps\\common"
    - "%PROGRAMFILES(X86)%\\Steam\\steamapps\\common"
    - "D:\\Games"
```

**Linux:**
```yaml
agent:
  game_folders:
    - "$HOME/.steam/steam/steamapps/common"
    - "$HOME/.local/share/Steam/steamapps/common"
    - "~/Games"
```

### Custom Commands

**Windows:**
```yaml
agent:
  custom_commands:
    open_steam: "C:\\Program Files (x86)\\Steam\\steam.exe"
    screenshot: "snippingtool"
    lock_pc: "rundll32.exe user32.dll,LockWorkStation"
```

**Linux:**
```yaml
agent:
  custom_commands:
    open_steam: "steam"
    screenshot: "gnome-screenshot"
    lock_screen: "loginctl lock-session"
```

## Permissions on Linux

Some operations require elevated privileges on Linux:

### Option 1: Run Service as Root (Simple but less secure)
```bash
sudo python3 scripts/install_systemd.py
```

### Option 2: Configure Passwordless Sudo (Recommended)

1. Edit sudoers file:
   ```bash
   sudo visudo
   ```

2. Add lines for your user:
   ```
   your_username ALL=(ALL) NOPASSWD: /sbin/shutdown
   your_username ALL=(ALL) NOPASSWD: /sbin/reboot
   your_username ALL=(ALL) NOPASSWD: /bin/systemctl suspend
   your_username ALL=(ALL) NOPASSWD: /bin/systemctl poweroff
   your_username ALL=(ALL) NOPASSWD: /bin/systemctl reboot
   ```

3. Save and restart the agent

### Option 3: Use Polkit (Advanced)

Create a polkit rule to allow shutdown/reboot without password.

## Testing Platform Detection

The agent automatically detects the platform:

```python
import sys
print(sys.platform)  # 'win32' on Windows, 'linux' on Linux
```

You can test platform-specific features:

```bash
# Test shutdown (will actually shutdown after delay!)
python3 -c "from main import HASSMQTTAgent; import sys; print(sys.platform)"

# Test in dry-run mode (if implemented)
python3 main.py --dry-run
```

## Troubleshooting

### Linux: "Permission denied" for power commands

**Problem:** Agent can't execute shutdown/reboot/suspend

**Solutions:**
1. Configure passwordless sudo (see above)
2. Run service as root
3. Use polkit rules

### Linux: GUI setup won't start

**Problem:** `tkinter` not found

**Solution:**
```bash
sudo apt-get install python3-tk
```

### Linux: Games not detected

**Problem:** Non-Windows executables not recognized

**Checklist:**
- Verify files have execute permission
- Check folder paths are correct
- Look in logs for scan results
- Test with `find ~/Games -type f -executable`

### Windows: Service won't install

**Problem:** `pywin32` not found or not configured

**Solution:**
```powershell
pip install pywin32
python Scripts/pywin32_postinstall.py -install
```

## Cross-Platform Development

When contributing cross-platform code:

1. **Test on both platforms** if possible
2. **Use os.path** instead of hardcoded paths
3. **Check sys.platform** for platform-specific code
4. **Use subprocess** carefully - commands differ between platforms
5. **Handle permissions** - Linux often needs sudo, Windows needs admin
6. **Environment variables** - Different on each platform

Example:
```python
import sys
import os

if sys.platform == "win32":
    # Windows-specific code
    game_folders = [
        os.path.join(os.environ['PROGRAMFILES(X86)'], 'Steam', 'steamapps', 'common')
    ]
elif sys.platform.startswith('linux'):
    # Linux-specific code  
    game_folders = [
        os.path.join(os.environ['HOME'], '.steam', 'steam', 'steamapps', 'common')
    ]
```

## Future Platform Support

Planned:
- macOS support (using launchd for service)
- BSD support
- Docker container support
- Raspberry Pi optimizations

## Getting Help

Platform-specific issues:
- Windows: See [Windows Troubleshooting](TROUBLESHOOTING.md#windows)
- Linux: See [Linux Troubleshooting](TROUBLESHOOTING.md#linux)

General support:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [scripts/README.md](scripts/README.md)
- Check the logs: `hass_mqtt_agent.log`

