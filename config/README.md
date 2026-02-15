# Configuration Files

This directory contains configuration file examples and templates for the HASS MQTT Agent.

## Files

### config.yaml.example

Template configuration file with all available options documented.

**To use:**

```bash
# Linux/macOS
cp config.yaml.example ../config.yaml

# Windows
copy config.yaml.example ..\config.yaml
```

Then edit `config.yaml` with your specific settings (MQTT broker, device name, etc.).

### homeassistant_examples.yaml

Example Home Assistant configurations including:
- Automations
- Scripts
- Dashboard cards
- Template sensors

These can be added to your Home Assistant `configuration.yaml` or individual YAML files.

## Configuration Wizard

Instead of manually editing config files, you can use the interactive setup wizards:

### GUI Wizard (Recommended)
```bash
python scripts/setup_config_gui.py
```

### Terminal Wizard
```bash
python scripts/setup_config.py
```

Both wizards will create a properly formatted `config.yaml` in the project root.

## Important Notes

- `config.yaml` (without .example) is gitignored - it contains your sensitive data
- Always keep `config.yaml.example` updated with new configuration options
- Platform-specific examples are included for both Windows and Linux

## Configuration Options

See the [main documentation](../docs/) for detailed configuration guides:
- [Quick Start](../docs/QUICKSTART.md) - Basic setup
- [Cross-Platform Guide](../docs/CROSS_PLATFORM.md) - Platform-specific config

## Example Configurations

### Minimal Configuration

```yaml
mqtt:
  broker: "192.168.1.100"
  port: 1883

homeassistant:
  device_name: "My PC"
  device_id: "my_pc_01"

agent:
  status_update_interval: 30
  game_folders: []
  custom_commands: {}
```

### Full Configuration

See `config.yaml.example` for a complete example with all options and detailed comments.

