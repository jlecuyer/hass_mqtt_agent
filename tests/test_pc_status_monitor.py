"""
Unit tests for PCStatusMonitor class
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import shutil


# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hass_mqtt_agent.main import PCStatusMonitor


class TestPCStatusMonitor(unittest.TestCase):
    """Test cases for PCStatusMonitor"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.game_folder = os.path.join(self.temp_dir, "games")
        os.makedirs(self.game_folder, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_empty_game_folders(self):
        """Test initialization with empty game folders"""
        monitor = PCStatusMonitor([])
        self.assertEqual(monitor.game_folders, [])
        self.assertEqual(len(monitor.game_executables), 0)

    def test_init_with_game_folders(self):
        """Test initialization with game folders"""
        monitor = PCStatusMonitor([self.game_folder])
        self.assertEqual(monitor.game_folders, [self.game_folder])

    @patch('sys.platform', 'win32')
    def test_scan_game_folders_windows(self):
        """Test scanning game folders on Windows"""
        # Create test executables
        game1 = os.path.join(self.game_folder, "game1.exe")
        game2 = os.path.join(self.game_folder, "game2.exe")
        non_game = os.path.join(self.game_folder, "readme.txt")

        Path(game1).touch()
        Path(game2).touch()
        Path(non_game).touch()

        monitor = PCStatusMonitor([self.game_folder])

        # Should find .exe files
        self.assertIn("game1.exe", monitor.game_executables)
        self.assertIn("game2.exe", monitor.game_executables)
        self.assertNotIn("readme.txt", monitor.game_executables)

    @patch('hass_mqtt_agent.main.os.access')
    @patch('sys.platform', 'linux')
    def test_scan_game_folders_linux(self, mock_access):
        """Test scanning game folders on Linux"""
        # Create test executables
        game1 = os.path.join(self.game_folder, "game1")
        non_executable = os.path.join(self.game_folder, "readme.txt")

        Path(game1).touch()
        Path(non_executable).touch()

        # Mock os.access to return True only for game1
        def access_side_effect(path, mode):
            if mode == os.X_OK:
                return 'game1' in path
            return True  # For other checks (F_OK, R_OK, etc.)

        mock_access.side_effect = access_side_effect

        monitor = PCStatusMonitor([self.game_folder])

        # Should find executable files
        self.assertIn("game1", monitor.game_executables)
        self.assertNotIn("readme.txt", monitor.game_executables)

    def test_scan_nonexistent_folder(self):
        """Test scanning a folder that doesn't exist"""
        nonexistent = os.path.join(self.temp_dir, "nonexistent")
        monitor = PCStatusMonitor([nonexistent])

        # Should handle gracefully
        self.assertEqual(len(monitor.game_executables), 0)

    @patch('psutil.process_iter')
    def test_is_game_running_true(self, mock_proc_iter):
        """Test detecting when a game is running"""
        # Create a mock process
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'game1.exe',
            'exe': os.path.join(self.game_folder, 'game1.exe')
        }
        mock_proc_iter.return_value = [mock_proc]

        monitor = PCStatusMonitor([self.game_folder])
        monitor.game_executables = {'game1.exe'}

        self.assertTrue(monitor.is_game_running())

    @patch('psutil.process_iter')
    def test_is_game_running_false(self, mock_proc_iter):
        """Test when no game is running"""
        # Create a mock process that's not a game
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'notepad.exe',
            'exe': 'C:\\Windows\\notepad.exe'
        }
        mock_proc_iter.return_value = [mock_proc]

        monitor = PCStatusMonitor([self.game_folder])
        monitor.game_executables = {'game1.exe'}

        self.assertFalse(monitor.is_game_running())

    @patch('psutil.process_iter')
    def test_is_game_running_no_executables(self, mock_proc_iter):
        """Test when no game executables are configured"""
        monitor = PCStatusMonitor([])
        self.assertFalse(monitor.is_game_running())

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_get_system_info(self, mock_memory, mock_cpu):
        """Test getting system information"""
        # Mock system stats
        mock_cpu.return_value = 45.5
        mock_memory_obj = MagicMock()
        mock_memory_obj.percent = 60.2
        mock_memory_obj.available = 8 * (1024**3)  # 8 GB
        mock_memory.return_value = mock_memory_obj

        monitor = PCStatusMonitor([])
        info = monitor.get_system_info()

        self.assertEqual(info['cpu_percent'], 45.5)
        self.assertEqual(info['memory_percent'], 60.2)
        self.assertEqual(info['memory_available_gb'], 8.0)

    def test_is_system_sleeping(self):
        """Test system sleeping check"""
        monitor = PCStatusMonitor([])
        # Currently always returns False
        self.assertFalse(monitor.is_system_sleeping())

    def test_rescan_game_folders(self):
        """Test rescanning game folders"""
        monitor = PCStatusMonitor([self.game_folder])
        initial_count = len(monitor.game_executables)

        # Add a new game
        if sys.platform == 'win32':
            new_game = os.path.join(self.game_folder, "newgame.exe")
        else:
            new_game = os.path.join(self.game_folder, "newgame")

        Path(new_game).touch()
        if sys.platform != 'win32':
            os.chmod(new_game, 0o755)

        monitor.rescan_game_folders()

        # Should find the new game
        self.assertGreater(len(monitor.game_executables), initial_count)


if __name__ == '__main__':
    unittest.main()

