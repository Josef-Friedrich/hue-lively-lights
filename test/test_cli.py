from _helper import config_file, command_name
from lively_lights import main
from unittest import mock
import subprocess
import unittest

usage = 'usage: {}'.format(command_name)


class TestCliUnit(unittest.TestCase):

    @mock.patch('sys.argv', ['t', 'info', 'daynight'])
    @mock.patch('lively_lights.Configuration')
    @mock.patch('lively_lights.DayNight')
    def test_info_daynight(self, day_night, config):
        main()
        day_night.return_value.overview.assert_called_with()


class TestCli(unittest.TestCase):

    def test_without_arguments(self):

        run = subprocess.run([command_name], encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue(usage in run.stderr)

    def test_help(self):
        run = subprocess.run([command_name, '-h'], encoding='utf-8',
                             stdout=subprocess.PIPE)
        self.assertEqual(run.returncode, 0)
        self.assertTrue(usage in run.stdout)

    def test_daynight(self):
        run = subprocess.run([command_name, '-c',  config_file,
                              'info', 'daynight'],
                             encoding='utf-8',
                             stdout=subprocess.PIPE)
        self.assertEqual(run.returncode, 0)
        self.assertTrue('Dawn' in run.stdout)
        self.assertTrue('Sunrise' in run.stdout)
        self.assertTrue('Noon' in run.stdout)
        self.assertTrue('Sunset' in run.stdout)
        self.assertTrue('Dusk' in run.stdout)
