"""
Pytest-specific tests using fixtures
These tests demonstrate pytest features and use the conftest.py fixtures
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hass_mqtt_agent.main import HASSMQTTAgent, PCStatusMonitor


class TestPCStatusMonitorPytest:
    """Pytest-style tests for PCStatusMonitor"""

    def test_init_with_game_folder_fixture(self, game_folder):
        """Test initialization with game folder fixture"""
        monitor = PCStatusMonitor([game_folder])
        assert monitor.game_folders == [game_folder]
        assert len(monitor.game_executables) >= 2  # Should find test games

    def test_system_info_returns_dict(self):
        """Test that system info returns a dictionary with expected keys"""
        monitor = PCStatusMonitor([])
        info = monitor.get_system_info()

        assert isinstance(info, dict)
        assert 'cpu_percent' in info
        assert 'memory_percent' in info
        assert 'memory_available_gb' in info

    @pytest.mark.parametrize("folders,expected_count", [
        ([], 0),
        (["/nonexistent"], 0),
    ])
    def test_init_with_various_folders(self, folders, expected_count):
        """Test initialization with various folder configurations"""
        monitor = PCStatusMonitor(folders)
        assert len(monitor.game_folders) == len(folders)

    def test_rescan_updates_executables(self, game_folder):
        """Test that rescanning finds new executables"""
        monitor = PCStatusMonitor([game_folder])
        initial_count = len(monitor.game_executables)

        # Create a new game
        import sys
        if sys.platform == 'win32':
            new_game = os.path.join(game_folder, "new_game.exe")
        else:
            new_game = os.path.join(game_folder, "new_game")

        with open(new_game, 'w') as f:
            f.write("")

        if sys.platform != 'win32':
            os.chmod(new_game, 0o755)

        monitor.rescan_game_folders()

        assert len(monitor.game_executables) > initial_count


class TestHASSMQTTAgentPytest:
    """Pytest-style tests for HASSMQTTAgent"""

    def test_config_loading(self, config_file):
        """Test configuration loading with fixture"""
        agent = HASSMQTTAgent(config_file)

        assert agent.config is not None
        assert agent.config['mqtt']['broker'] == '192.168.1.100'
        assert agent.config['homeassistant']['device_name'] == 'Test PC'

    def test_topics_are_properly_formatted(self, config_file):
        """Test MQTT topics are properly formatted"""
        agent = HASSMQTTAgent(config_file)

        assert agent.base_topic == 'hass_agent/test_pc'
        assert agent.availability_topic == 'hass_agent/test_pc/availability'
        assert agent.state_topic == 'hass_agent/test_pc/state'
        assert agent.command_topic == 'hass_agent/test_pc/command'

    @pytest.mark.parametrize("command,expected_call", [
        ("shutdown", "_shutdown_pc"),
        ("reboot", "_reboot_pc"),
        ("sleep", "_sleep_pc"),
    ])
    def test_command_execution_routing(self, config_file, command, expected_call):
        """Test that commands are routed to correct methods"""
        agent = HASSMQTTAgent(config_file)

        with patch.object(agent, expected_call) as mock_method:
            agent._execute_command(command)
            mock_method.assert_called_once()

    def test_custom_command_execution(self, config_file):
        """Test custom command execution"""
        agent = HASSMQTTAgent(config_file)

        with patch('subprocess.Popen') as mock_popen:
            agent._execute_command('custom:test_cmd')
            mock_popen.assert_called_once()

            # Verify command string
            call_args = mock_popen.call_args
            assert call_args[0][0] == 'echo test'
            assert call_args[1]['shell'] is True

    @patch('paho.mqtt.client.Client')
    def test_state_publish_format(self, mock_client_class, config_file):
        """Test that published state has correct format"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        agent = HASSMQTTAgent(config_file)
        agent.mqtt_client = mock_client
        agent.status_monitor = MagicMock()

        # Mock status monitor responses
        agent.status_monitor.is_game_running.return_value = True
        agent.status_monitor.is_system_sleeping.return_value = False
        agent.status_monitor.get_system_info.return_value = {
            'cpu_percent': 45.0,
            'memory_percent': 55.0,
            'memory_available_gb': 10.0
        }

        agent._publish_state()

        # Verify publish was called
        assert mock_client.publish.called

        # Extract and verify state
        call_args = mock_client.publish.call_args[0]
        state_topic = call_args[0]
        state_json = call_args[1]

        assert state_topic == agent.state_topic

        state = json.loads(state_json)
        assert state['status'] == 'online'
        assert state['game_running'] is True
        assert state['sleeping'] is False
        assert state['cpu_percent'] == 45.0

    @patch('paho.mqtt.client.Client')
    def test_discovery_messages_contain_device_info(self, mock_client_class, config_file):
        """Test that discovery messages include device information"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        agent = HASSMQTTAgent(config_file)
        agent.mqtt_client = mock_client

        agent._publish_discovery()

        # Check that multiple discovery messages were published
        assert mock_client.publish.call_count >= 6

        # Verify device info in at least one message
        for call in mock_client.publish.call_args_list:
            topic = call[0][0]
            if '/config' in topic:
                payload = json.loads(call[0][1])
                if 'device' in payload:
                    device = payload['device']
                    assert 'identifiers' in device
                    assert 'name' in device
                    assert device['name'] == 'Test PC'
                    break


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_missing_config_file(self):
        """Test handling of missing configuration file"""
        with pytest.raises(SystemExit):
            HASSMQTTAgent('nonexistent_file.yaml')

    def test_empty_game_folder_list(self):
        """Test handling of empty game folder list"""
        monitor = PCStatusMonitor([])
        assert monitor.is_game_running() is False

    @patch('psutil.process_iter')
    def test_process_access_denied(self, mock_proc_iter):
        """Test handling of process access denied"""
        import psutil

        # Mock process that raises AccessDenied
        mock_proc = MagicMock()
        mock_proc.info.side_effect = psutil.AccessDenied()
        mock_proc_iter.return_value = [mock_proc]

        monitor = PCStatusMonitor([])
        monitor.game_executables = {'game.exe'}

        # Should handle gracefully
        result = monitor.is_game_running()
        assert result is False


@pytest.mark.slow
class TestSlowTests:
    """Tests that take longer to run"""

    def test_game_folder_scan_performance(self, temp_dir):
        """Test performance of scanning large game folders"""
        import time

        # Create many fake games
        games_dir = os.path.join(temp_dir, 'many_games')
        os.makedirs(games_dir)

        for i in range(100):
            if sys.platform == 'win32':
                game = os.path.join(games_dir, f"game_{i}.exe")
            else:
                game = os.path.join(games_dir, f"game_{i}")

            with open(game, 'w') as f:
                f.write("")

            if sys.platform != 'win32':
                os.chmod(game, 0o755)

        start_time = time.time()
        monitor = PCStatusMonitor([games_dir])
        elapsed = time.time() - start_time

        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0
        assert len(monitor.game_executables) == 100

