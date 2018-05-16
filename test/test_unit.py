from _helper import config_file
from unittest import mock
import lively_lights
import os
import unittest
import time


class TestClassHue(unittest.TestCase):

    @mock.patch('lively_lights.Bridge')
    def test_environ(self, bridge):
        os.environ['LL_BRIDGE_IP'] = '1.2.3.4'
        os.environ['LL_BRIDGE_USERNAME'] = 'test'

        lively_lights.Hue(config_environ_prefix='LL')
        bridge.assert_called_with('1.2.3.4', 'test', colorize_output=False,
                                  verbosity_level=0)

    @mock.patch('lively_lights.Bridge')
    def test_ini(self, bridge):
        lively_lights.Hue(config_environ_prefix='XX',
                          config_file_path=config_file)
        bridge.assert_called_with('192.168.3.60', 'joseffriedrich',
                                  colorize_output=False, verbosity_level=0)


class TestClassConfiguration(unittest.TestCase):

    def test_environ(self):
        os.environ['AAA_BRIDGE_IP'] = '1.2.3.4'
        os.environ['AAA_BRIDGE_USERNAME'] = 'test'
        config = lively_lights.Configuration(config_environ_prefix='AAA')
        self.assertEqual(config.get('bridge', 'ip'), '1.2.3.4')
        self.assertEqual(config.get('bridge', 'username'), 'test')


class TestClassDayNight(unittest.TestCase):

    def test_day_light(self):
        config = lively_lights.Configuration(config_file_path=config_file)
        day_light = lively_lights.DayNight(config)
        self.assertTrue(day_light)


class TestClassSceneSequence(unittest.TestCase):

    @mock.patch('lively_lights.set_light_multiple', mock.Mock())
    def test_time_out(self):
        reachable_lights = mock.Mock()
        reachable_lights.list.return_value = [mock.Mock(), mock.Mock()]
        scene = lively_lights.SceneSequence(mock.Mock(), reachable_lights)
        begin = time.time()
        scene.start(10)
        end = time.time()
        self.assertTrue(end - begin <= 10)
