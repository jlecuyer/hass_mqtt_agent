# Home Assistant MQTT Agent
Control your PC from Home Assistant via MQTT. Cross-platform (Windows/Linux).
## Features
- 🎮 **Remote Control** - Shutdown, reboot, sleep from Home Assistant
- 📊 **Monitoring** - CPU, memory, game detection
- 🔌 **Auto-discovery** - Shows up automatically in Home Assistant
- 🖥️ **Cross-platform** - Works on Windows and Linux
## Quick Start
### 1. Install
```bash
pip install -r requirements.txt
```
### 2. Configure
```bash
python main.py
# Choose option 1 (GUI) or 2 (terminal) for setup wizard
```
Or copy and edit manually:
```bash
cp config/config.yaml.example config.yaml
nano config.yaml  # Add your MQTT broker IP
```
### 3. Run
```bash
python main.py
```
That's it! Check Home Assistant for a new device.
## Install as Service
**Windows:**
```powershell
.\scripts\install_windows.ps1
```
**Linux:**
```bash
sudo python scripts/install_systemd.py
```
## Configuration Example
```yaml
mqtt:
  broker: "192.168.1.100"
  port: 1883
  username: "mqtt_user"  # Optional
  password: "mqtt_pass"  # Optional
homeassistant:
  device_name: "My PC"
  device_id: "my_pc"
agent:
  status_update_interval: 30
  # Folders to scan for games
  game_folders:
    - "C:\\Program Files (x86)\\Steam\\steamapps\\common"  # Windows
    - "~/.steam/steam/steamapps/common"                     # Linux
```
## What You Get in Home Assistant
**Buttons:**
- Shutdown
- Reboot  
- Sleep
**Sensors:**
- Online/Offline status
- CPU usage
- Memory usage
- Game running (yes/no)
## Documentation
- [QUICKSTART.md](docs/QUICKSTART.md) - Detailed setup
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- [CROSS_PLATFORM.md](docs/CROSS_PLATFORM.md) - Platform differences
- [BUILD.md](docs/BUILD.md) - Build from source
## Requirements
- Python 3.10+
- MQTT Broker (Mosquitto)
- Home Assistant
## License
MIT
