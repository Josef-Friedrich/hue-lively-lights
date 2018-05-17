from _helper import config_file, command_name
from lively_lights import main
from unittest import mock
import subprocess
import unittest

usage = 'usage: {}'.format(command_name)


class TestCliUnit(unittest.TestCase):

    @mock.patch('sys.argv', ['.', 'info', 'daynight'])
    @mock.patch('lively_lights.Configuration', mock.Mock())
    @mock.patch('lively_lights.DayNight')
    def test_info_daynight(self, day_night):
        main()
        day_night.return_value.overview.assert_called_with()

    # @mock.patch('sys.argv', [
    #     '.', 'scene', 'pendulum',
    #     '--color1', '1', '--color2', '2',
    #     '--lights1', '1', '2', '--lights2', '3', '4',
    #     '--sleep-time', '1',
    #     '--transition-time', '1',
    # ])
    # @mock.patch('lively_lights.Configuration', mock.Mock())
    # @mock.patch('lively_lights.Hue', mock.Mock())
    # @mock.patch('lively_lights.ScenePendulum')
    # def test_scene_pendulum(self, Scene):
    #     main()
    #     self.assertEqual(Scene.call_args[1], {
    #         'color_1': 1,
    #         'color_2': 2,
    #         'lights_1': ['1', '2'],
    #         'lights_2': ['3', '4'],
    #         'sleep_time': float(1),
    #         'transition_time': float(1),
    #     })
    #
    # @mock.patch('sys.argv', [
    #     '.', 'scene', 'sequence',
    #     '--brightness', '1',
    #     '--hue-sequence', '1', '2',
    #     '--sleep-time', '1',
    #     '--transition-time', '1',
    # ])
    # @mock.patch('lively_lights.Configuration', mock.Mock())
    # @mock.patch('lively_lights.Hue', mock.Mock())
    # @mock.patch('lively_lights.SceneSequence')
    # def test_scene_sequence(self, Scene):
    #     main()
    #     self.assertEqual(Scene.call_args[1], {
    #         'brightness': 1,
    #         'hue_sequence': ['1', '2'],
    #         'sleep_time': float(1),
    #         'transition_time': float(1),
    #     })


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
