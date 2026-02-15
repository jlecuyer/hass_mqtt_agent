"""
Integration tests for HASS MQTT Agent
Tests the full agent workflow
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import yaml
import time
import threading


# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hass_mqtt_agent.main import HASSMQTTAgent, PCStatusMonitor


class TestIntegration(unittest.TestCase):
    """Integration test cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            'mqtt': {
                'broker': '192.168.1.100',
                'port': 1883,
                'username': 'test_user',
                'password': 'test_pass',
                'client_id': 'test_client'
            },
            'homeassistant': {
                'discovery_prefix': 'homeassistant',
                'device_name': 'Test PC',
                'device_id': 'test_pc'
            },
            'agent': {
                'game_folders': [],
                'status_update_interval': 1,  # Fast for testing
                'custom_commands': {}
            }
        }

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)

    @patch('paho.mqtt.client.Client')
    @patch('hass_mqtt_agent.main.PCStatusMonitor')
    def test_full_agent_lifecycle(self, mock_monitor_class, mock_mqtt_client):
        """Test complete agent lifecycle: start, run, stop"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client

        mock_monitor = MagicMock()
        mock_monitor.is_game_running.return_value = False
        mock_monitor.is_system_sleeping.return_value = False
        mock_monitor.get_system_info.return_value = {
            'cpu_percent': 50.0,
            'memory_percent': 60.0,
            'memory_available_gb': 8.0
        }
        mock_monitor_class.return_value = mock_monitor

        agent = HASSMQTTAgent(self.temp_config.name)

        # Start agent
        agent.start()
        self.assertTrue(agent.running)

        # Let it run for a bit
        time.sleep(2)

        # Verify MQTT operations occurred
        mock_client.connect.assert_called_once()
        mock_client.loop_start.assert_called_once()

        # Stop agent
        agent.stop()
        self.assertFalse(agent.running)

    @patch('paho.mqtt.client.Client')
    def test_command_processing_flow(self, mock_mqtt_client):
        """Test command processing from MQTT to execution"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client

        agent = HASSMQTTAgent(self.temp_config.name)
        agent.mqtt_client = mock_client

        # Simulate receiving a command
        mock_msg = MagicMock()
        mock_msg.payload = b'shutdown'

        with patch('subprocess.run') as mock_run:
            agent._on_message(None, None, mock_msg)
            # Should execute shutdown command
            mock_run.assert_called_once()

    @patch('paho.mqtt.client.Client')
    @patch('hass_mqtt_agent.main.PCStatusMonitor')
    def test_status_update_loop(self, mock_monitor_class, mock_mqtt_client):
        """Test status update loop publishes periodically"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client

        mock_monitor = MagicMock()
        mock_monitor.is_game_running.return_value = False
        mock_monitor.is_system_sleeping.return_value = False
        mock_monitor.get_system_info.return_value = {
            'cpu_percent': 50.0,
            'memory_percent': 60.0,
            'memory_available_gb': 8.0
        }
        mock_monitor_class.return_value = mock_monitor

        agent = HASSMQTTAgent(self.temp_config.name)
        agent.mqtt_client = mock_client
        agent.status_monitor = mock_monitor

        # Start the status loop
        agent.running = True
        status_thread = threading.Thread(target=agent._status_update_loop, daemon=True)
        status_thread.start()

        # Let it run for a few cycles
        time.sleep(3)

        # Stop the loop
        agent.running = False
        status_thread.join(timeout=2)

        # Should have published state multiple times
        self.assertGreater(mock_client.publish.call_count, 1)

    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config should load
        agent = HASSMQTTAgent(self.temp_config.name)
        self.assertIsNotNone(agent.config)

        # Invalid config should fail
        with self.assertRaises(SystemExit):
            HASSMQTTAgent('nonexistent.yaml')


if __name__ == '__main__':
    unittest.main()

