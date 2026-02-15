# Quick Start Guide

Get your Home Assistant MQTT PC Agent running in 5 minutes!

## Prerequisites

- [ ] Windows PC (Windows 10/11)
- [ ] Python 3.10 or higher installed
- [ ] MQTT broker running (usually on Home Assistant)
- [ ] Home Assistant with MQTT integration configured
- [ ] PC connected to network via ethernet

## Step 1: Download & Install (2 min)

### Option A: Using PowerShell Script (Easiest)

1. Right-click `install.ps1` → **Run with PowerShell as Administrator**
2. Follow the prompts
3. Done! Skip to Step 4.

### Option B: Manual Installation

1. Open PowerShell as Administrator

2. Install Python packages:
   ```powershell
   pip install -r requirements.txt
   ```

## Step 2: Configure (1 min)

1. Edit `config.yaml`:
   ```powershell
   notepad config.yaml
   ```

2. Update at minimum:
   ```yaml
   mqtt:
     broker: "192.168.1.100"  # ← Your MQTT broker IP
   ```

3. Optional: Add your MQTT username/password if required

4. Optional: Customize device name
   ```yaml
   homeassistant:
     device_name: "Gaming PC"  # ← Change this
   ```

## Step 3: Test (1 min)

Run in console mode to verify everything works:

```powershell
python main.py
```

You should see:
```
Home Assistant MQTT Agent
==================================================
Connected to MQTT broker
Subscribed to hass_agent/gaming_pc_01/command
Published Home Assistant discovery messages
HASS MQTT Agent started successfully

Agent is running. Press Ctrl+C to stop.
```

**Check Home Assistant:**
- Go to Settings → Devices & Services → MQTT
- You should see a new device (e.g., "Gaming PC")
- Click on it to see sensors and buttons

If it works, press Ctrl+C to stop.

## Step 4: Install as Service (1 min)

**In PowerShell as Administrator:**

```powershell
# Install the service
python main.py install

# Start the service
python main.py start
```

**Verify it's running:**
- Open Services: Win+R → `services.msc`
- Find "Home Assistant MQTT Agent"
- Status should be "Running"
- Startup Type should be "Automatic"

## Step 5: Use It! (30 sec)

**In Home Assistant:**

1. Go to Settings → Devices & Services → MQTT
2. Find your PC device
3. Click on it to see:
   - 📊 Status sensor (online/offline)
   - 🎮 Game Running sensor
   - 💻 CPU usage sensor
   - 🧠 Memory usage sensor
   - 🔴 Shutdown button
   - 🔄 Reboot button
   - 😴 Sleep button

4. Test a button - try the Sleep button!

## Troubleshooting

### "Config file not found"
→ Make sure `config.yaml` exists (not `config.yaml.example`)

### "Failed to connect to MQTT broker"
→ Check the broker IP in config.yaml
→ Verify MQTT broker is running
→ Test with: `ping 192.168.1.100` (your broker IP)

### Service won't start
→ Check `hass_mqtt_agent.log` in the installation folder
→ Make sure config.yaml is in the same folder as main.py

### Entities not appearing in Home Assistant
→ Wait 30 seconds
→ Restart the agent: `python main.py restart`
→ Check MQTT integration is working in HA

## Next Steps

### Enable Wake-on-LAN

**In BIOS:**
1. Reboot → Enter BIOS (usually F2, F12, or DEL during boot)
2. Find "Wake on LAN" or "Resume by PCI-E" → Enable it
3. Save and exit

**In Windows:**
1. Device Manager → Network Adapters
2. Right-click your adapter → Properties
3. Power Management tab:
   - ✓ Allow this device to wake the computer
   - ✓ Only allow a magic packet to wake
4. Advanced tab:
   - Wake on Magic Packet → Enabled

**Get your MAC address:**
```powershell
ipconfig /all
# Look for "Physical Address" under your ethernet adapter
# Example: AA-BB-CC-DD-EE-FF
```

**In Home Assistant:**
```yaml
# configuration.yaml
wake_on_lan:

# automation.yaml
automation:
  - alias: "Wake PC"
    trigger:
      - platform: state
        entity_id: input_button.wake_pc
    action:
      - service: wake_on_lan.send_magic_packet
        data:
          mac: "AA:BB:CC:DD:EE:FF"  # Your MAC here
```

### Add Game Detection

1. Find where your games are installed (common locations):
   - Steam: `C:\Program Files (x86)\Steam\steamapps\common`
   - Epic Games: `C:\Program Files\Epic Games`
   - Xbox: `C:\XboxGames`
   - Additional Steam libraries: Check Steam Settings > Downloads > Steam Library Folders

2. Edit `config.yaml`:
   ```yaml
   agent:
     game_folders:
       - "C:\\Program Files (x86)\\Steam\\steamapps\\common"
       - "D:\\SteamLibrary\\steamapps\\common"  # If you have multiple drives
       - "C:\\Program Files\\Epic Games"
       - "C:\\XboxGames"
   ```
   
3. Restart service: `python main.py restart`

The agent will scan these folders at startup and detect when any game executable runs.
After installing new games, restart the service to rescan.

### Create Automations

See `homeassistant_examples.yaml` for ready-to-use automations:
- Auto-shutdown when leaving home
- Wake PC in the morning
- Notify when game starts
- And more!

## Service Management Commands

```powershell
# All commands require Administrator privileges

python main.py install   # Install as Windows service
python main.py start     # Start the service
python main.py stop      # Stop the service
python main.py restart   # Restart the service
python main.py remove    # Uninstall the service
python main.py           # Run in console mode (for testing)
```

## Getting Help

1. **Check the log:** Open `hass_mqtt_agent.log`
2. **Read docs:** See `README.md` for detailed info
3. **Troubleshooting:** See `TROUBLESHOOTING.md` for common issues
4. **Architecture:** See `ARCHITECTURE.md` to understand how it works
5. **Examples:** See `homeassistant_examples.yaml` for automation ideas

## Files Reference

| What                  | Where                          |
|-----------------------|--------------------------------|
| Main code             | `main.py`                      |
| Configuration         | `config.yaml`                  |
| Logs                  | `hass_mqtt_agent.log`          |
| Full documentation    | `README.md`                    |
| HA examples           | `homeassistant_examples.yaml`  |
| Troubleshooting       | `TROUBLESHOOTING.md`           |
| Architecture info     | `ARCHITECTURE.md`              |

## Success Checklist

- [ ] Python and packages installed
- [ ] config.yaml configured with MQTT broker IP
- [ ] Tested in console mode - connects successfully
- [ ] Installed as Windows service
- [ ] Service is running
- [ ] Device appears in Home Assistant
- [ ] Can see sensors updating
- [ ] Buttons work (tested sleep or shutdown)
- [ ] (Optional) Wake-on-LAN configured and tested

---

**You're all set! Enjoy controlling your PC from Home Assistant! 🎉**

For advanced usage, customization, and troubleshooting, see the other documentation files.


