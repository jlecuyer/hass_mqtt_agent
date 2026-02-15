"""
HASS MQTT Agent - Cross-platform PC control for Home Assistant via MQTT
"""

__version__ = "0.1.0"
__author__ = "Home Assistant MQTT Agent Contributors"
__license__ = "MIT"

from .main import HASSMQTTAgent, PCStatusMonitor

__all__ = ["HASSMQTTAgent", "PCStatusMonitor", "__version__"]

