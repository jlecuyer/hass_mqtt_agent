#!/usr/bin/env python3
"""
HASS MQTT Agent - Entry Point
This is a simple launcher that imports and runs the main agent.
The actual implementation is in src/hass_mqtt_agent/main.py
"""
import sys
from pathlib import Path
# Add src to path for development mode
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))
# Import and run the main agent
from hass_mqtt_agent.main import main
if __name__ == '__main__':
    main()
