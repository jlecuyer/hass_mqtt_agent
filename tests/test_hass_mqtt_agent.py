"""
Unit tests for HASSMQTTAgent class
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import json
import tempfile
import yaml


# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hass_mqtt_agent.main import HASSMQTTAgent


class TestHASSMQTTAgent(unittest.TestCase):
    """Test cases for HASSMQTTAgent"""

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
                'game_folders': ['/games'],
                'status_update_interval': 30,
                'custom_commands': {
                    'test_cmd': 'echo test'
                }
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

    def test_load_config_success(self):
        """Test successful config loading"""
        agent = HASSMQTTAgent(self.temp_config.name)
        self.assertEqual(agent.config['mqtt']['broker'], '192.168.1.100')
        self.assertEqual(agent.config['homeassistant']['device_name'], 'Test PC')

    def test_load_config_missing_file(self):
        """Test loading missing config file"""
        with self.assertRaises(SystemExit):
            HASSMQTTAgent('nonexistent.yaml')

    def test_topic_initialization(self):
        """Test MQTT topic initialization"""
        agent = HASSMQTTAgent(self.temp_config.name)
        self.assertEqual(agent.base_topic, 'hass_agent/test_pc')
        self.assertEqual(agent.availability_topic, 'hass_agent/test_pc/availability')
        self.assertEqual(agent.state_topic, 'hass_agent/test_pc/state')
        self.assertEqual(agent.command_topic, 'hass_agent/test_pc/command')

    @patch('paho.mqtt.client.Client')
    def test_setup_mqtt(self, mock_mqtt_client):
        """Test MQTT setup"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client

        agent = HASSMQTTAgent(self.temp_config.name)
        agent._setup_mqtt()

        # Verify client configuration
        mock_mqtt_client.assert_called_once()
        mock_client.username_pw_set.assert_called_once_with('test_user', 'test_pass')
        mock_client.will_set.assert_called_once()
        mock_client.connect.assert_called_once_with('192.168.1.100', 1883, 60)

    @patch('paho.mqtt.client.Client')
    def test_on_connect(self, mock_mqtt_client):
        """Test MQTT on_connect callback"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client

        agent = HASSMQTTAgent(self.temp_config.name)
        agent._setup_mqtt()

        # Simulate connection
        agent._on_connect(mock_client, None, None, 0)

        # Verify subscriptions and publications
        mock_client.subscribe.assert_called_once()
        self.assertTrue(mock_client.publish.called)

    def test_execute_command_shutdown(self):
        """Test shutdown command execution"""
        agent = HASSMQTTAgent(self.temp_config.name)

        with patch('subprocess.run') as mock_run:
            agent._execute_command('shutdown')
            mock_run.assert_called_once()

    def test_execute_command_reboot(self):
        """Test reboot command execution"""
        agent = HASSMQTTAgent(self.temp_config.name)

        with patch('subprocess.run') as mock_run:
            agent._execute_command('reboot')
            mock_run.assert_called_once()

    def test_execute_command_sleep(self):
        """Test sleep command execution"""
        agent = HASSMQTTAgent(self.temp_config.name)

        with patch('subprocess.run') as mock_run:
            agent._execute_command('sleep')
            mock_run.assert_called_once()

    def test_execute_custom_command(self):
        """Test custom command execution"""
        agent = HASSMQTTAgent(self.temp_config.name)

        with patch('subprocess.Popen') as mock_popen:
            agent._execute_command('custom:test_cmd')
            mock_popen.assert_called_once_with('echo test', shell=True)

    def test_execute_unknown_command(self):
        """Test unknown command handling"""
        agent = HASSMQTTAgent(self.temp_config.name)

        with patch('subprocess.run') as mock_run:
            agent._execute_command('unknown_command')
            # Should not execute anything
            mock_run.assert_not_called()

    @patch('paho.mqtt.client.Client')
    def test_publish_discovery(self, mock_mqtt_client):
        """Test Home Assistant discovery message publication"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client

        agent = HASSMQTTAgent(self.temp_config.name)
        agent.mqtt_client = mock_client
        agent._publish_discovery()

        # Should publish multiple discovery messages
        self.assertGreater(mock_client.publish.call_count, 5)

        # Verify at least one discovery message contains correct info
        calls = mock_client.publish.call_args_list
        found_status_sensor = False
        for call_args in calls:
            topic = call_args[0][0]
            if 'sensor' in topic and 'status' in topic:
                found_status_sensor = True
                payload = json.loads(call_args[0][1])
                self.assertEqual(payload['name'], 'Test PC Status')
                break

        self.assertTrue(found_status_sensor, "Status sensor discovery message not found")

    @patch('hass_mqtt_agent.main.PCStatusMonitor')
    @patch('paho.mqtt.client.Client')
    def test_publish_state(self, mock_mqtt_client, mock_monitor_class):
        """Test state publication"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client

        mock_monitor = MagicMock()
        mock_monitor.is_game_running.return_value = True
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

        agent._publish_state()

        # Verify state was published
        mock_client.publish.assert_called_once()
        call_args = mock_client.publish.call_args[0]
        state = json.loads(call_args[1])

        self.assertEqual(state['status'], 'online')
        self.assertTrue(state['game_running'])
        self.assertFalse(state['sleeping'])
        self.assertEqual(state['cpu_percent'], 50.0)

    @patch('hass_mqtt_agent.main.PCStatusMonitor')
    @patch('paho.mqtt.client.Client')
    def test_start_stop(self, mock_mqtt_client, mock_monitor_class):
        """Test agent start and stop"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        agent = HASSMQTTAgent(self.temp_config.name)

        # Start agent
        agent.start()
        self.assertTrue(agent.running)
        mock_client.loop_start.assert_called_once()

        # Stop agent
        agent.stop()
        self.assertFalse(agent.running)
        mock_client.loop_stop.assert_called_once()
        mock_client.disconnect.assert_called_once()

    def test_on_message(self):
        """Test MQTT message callback"""
        agent = HASSMQTTAgent(self.temp_config.name)

        mock_msg = MagicMock()
        mock_msg.payload = b'shutdown'

        with patch.object(agent, '_execute_command') as mock_execute:
            agent._on_message(None, None, mock_msg)
            mock_execute.assert_called_once_with('shutdown')

    @patch('subprocess.run')
    @patch('sys.platform', 'win32')
    def test_shutdown_windows(self, mock_run):
        """Test Windows shutdown command"""
        agent = HASSMQTTAgent(self.temp_config.name)
        agent._shutdown_pc()

        # Verify Windows shutdown command
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn('shutdown', args)
        self.assertIn('/s', args)

    @patch('subprocess.run')
    @patch('sys.platform', 'linux')
    def test_shutdown_linux(self, mock_run):
        """Test Linux shutdown command"""
        agent = HASSMQTTAgent(self.temp_config.name)
        agent._shutdown_pc()

        # Verify Linux shutdown command
        mock_run.assert_called()

    @patch('subprocess.run')
    @patch('sys.platform', 'win32')
    def test_reboot_windows(self, mock_run):
        """Test Windows reboot command"""
        agent = HASSMQTTAgent(self.temp_config.name)
        agent._reboot_pc()

        # Verify Windows reboot command
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn('shutdown', args)
        self.assertIn('/r', args)


if __name__ == '__main__':
    unittest.main()

