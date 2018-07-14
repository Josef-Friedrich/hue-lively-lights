"""Gather informations about the environment `lively_lights` is running in."""

from ping3 import ping
import astral
import datetime
import pyowm
import socket
import time
import platform
import subprocess


class HostUp(object):

    timeout = 3

    def ping_ping3(host, timeout=3):
        if ping(host, timeout=3):
            return True
        else:
            return False

    def _ping_external_command(self, host):
        option = "-n" if platform.system().lower() == "windows" else "-c"
        need_sh = True if platform.system().lower() == "windows" else False
        return subprocess.call(['ping', option, '1', host], shell=need_sh,
                               timeout=self.timeout) == 0

    def open_port(host, port, timeout=3):
        """
        https://stackoverflow.com/a/33117579
        :param string host: ipv4 address
        :param int port: open port
        :param in timeout: Timeout in seconds
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host,
                                                                       port))
            return True
        except Exception:
            return False


def is_host_pingable(host, timeout=3):
    if ping(host, timeout=3):
        return True
    else:
        return False


def is_host_reachable(host, port, timeout=3):
    """
    https://stackoverflow.com/a/33117579
    :param string host: ipv4 address
    :param int port: open port
    :param in timeout: Timeout in seconds
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


class DayNight(object):

    def __init__(self, latitude, longitude, timezone, elevation):
        self._location = astral.Location((
            'name',
            'region',
            latitude,
            longitude,
            timezone,
            elevation,
        ))

    def _sunrise(self):
        return self._location.sunrise()

    def _sunset(self):
        return self._location.sunset()

    def is_day(self):
        sunrise = self._sunrise()
        return sunrise < datetime.datetime.now(sunrise.tzinfo) < self._sunset()

    def is_night(self):
        return not self.is_day()

    def overview(self):
        sun = self._location.sun()
        out = 'Dawn:    {}\n' + \
              'Sunrise: {}\n' + \
              'Noon:    {}\n' + \
              'Sunset:  {}\n' + \
              'Dusk:    {}'

        return out.format(sun['dawn'], sun['sunrise'], sun['noon'],
                          sun['sunset'], sun['dusk'])


class Weather(object):
    """Gather weather informations about a given coordinate.

    :param string openweathermap_api_key:
      https://home.openweathermap.org/api_keys
    :param float latitude: e. g. 49.455556
    :param float longitude: e. g. 11.078611
    """

    def __init__(self, openweathermap_api_key, latitude, longitude):
        owm = pyowm.OWM(openweathermap_api_key)
        observation_list = owm.weather_around_coords(
            latitude,
            longitude,
        )
        observation = observation_list[0]
        self._location = observation.get_location()
        self._weather = observation.get_weather()

    def get_wind(self):
        """{'speed': 4.6, 'deg': 330}"""
        wind = self._weather.get_wind()
        return wind['speed']

    def get_temperature(self):
        """{'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}"""
        temperature = self._weather.get_temperature('celsius')
        return temperature['temp']


class ReachableLights(object):
    """
    :param bridge: The bridge object.
    :type bridge: lively_lights.phue.Bridge

    :param day_night: A DayNight object.
    :type day_night: lively_lights.DayNight

    :param list light_ids: Light IDs to filter the output of the methods
      :class:`lively_lights.ReachableLights.get_light_objects` and
      :class:`lively_lights.ReachableLights.get_light_ids`.

    :param int refresh_interval: Search every n seconds for new lights.

    :param bool not_at_night: Return light IDs not at night.

    :param bool not_during_daytime: Return light IDs not during at day.

    :param string check_open_port: Check if a host has an open TCP port:
      e. g. 192.168.3.11:22

    :param bool on_open_port: This parameter only takes effect if the parameter
      `check_open_port` is not empty.

    :param string check_ping: Check if a host is pingable. You have to be root
       e. g. 192.168.3.11

    :param bool on_ping: This parameter only takes effect if the parameter
      `check_ping` is not empty.
    """
    def __init__(self, bridge, day_night, light_ids=None, refresh_interval=60,
                 not_at_night=False, not_during_daytime=False,
                 check_open_port=None, on_open_port=True, check_ping=None,
                 on_ping=True, turn_off=False):

        self.light_ids = light_ids
        """A list of light IDS. """

        self.refresh_interval = refresh_interval
        """Search every n seconds for new lights."""

        self.not_at_night = not_at_night
        """Return light IDs only at night."""

        self.not_during_daytime = not_during_daytime
        """Return light IDs only at day."""

        self.check_open_port = check_open_port
        """Check if a host has an open TCP port: e. g. 192.168.3.11:22"""

        self.on_open_port = on_open_port
        """This parameter only takes effect if the parameter `check_open_port`
        is not empty."""

        self.check_ping = on_ping
        """Check if a host is pingable. You have to be root e. g.
          192.168.3.11"""

        self.turn_off = turn_off
        """Turn off lights on certain conditions."""

        self._current_light_index = 0
        """Needed for the foor loop iteration."""

        self._day_night = day_night
        """A DayNight object :class:`lively_lights.DayNight`"""

        self._bridge = bridge
        """The bridge object :class:`lively_lights.phue.Bridge`"""

        self._lights_refresh_state = {}
        """Cache for light reachable states. To avoid querying for reachable
        lights every time.

        .. code-block:: python

            self._lights_refresh_state = {
                1: (1530997150.9431288, True),
                2: (1530997179.6412678, False),
            }

        """

        self._lights_turn_off_state = {}
        """Cache for light turn off states. To avoid turning off the lights
        every time.

        .. code-block:: python

            self._lights_refresh_state = {
                1: 1530997150.9431288,
                2: 1530997179.6412678,
            }

        """

        self._lights = []
        """A list of light objects. Needed for the for loop iteration."""

        self._lights_count = 0
        """Count of reachable lights."""

    def __iter__(self):
        self._lights = self.get_light_objects()
        self._lights_count = len(self._lights)
        self._current_light_index = 0
        return self

    def __next__(self):
        current = self._current_light_index
        self._current_light_index += 1
        if current >= self._lights_count:
            raise StopIteration
        return self._lights[current]

    def _list_light_ids(self):
        """Build a list of light ids. If light_ids is set, return light_ids,
        else return all light ids from the bridge."""
        if self.light_ids:
            return self.light_ids
        else:
            light_ids = []
            for light in self._bridge.lights:
                light_ids.append(light.light_id)
            return light_ids

    def _turn_off_light(self, light_id):
        state = self._lights_turn_off_state
        if light_id not in state or (light_id in state and
           time.time() - state[light_id] < self.refresh_interval):
            self._bridge[light_id].on = False
            state[light_id] = time.time()

    def _turn_off_lights(self):
        for light_id in self._list_light_ids():
            self._turn_off_light(light_id)

    def _get_reachable(self):
        lights = []

        if (self.not_at_night and self._day_night.is_night()) or \
           (self.not_during_daytime and self._day_night.is_day()):
            if self.turn_off:
                self._turn_off_lights()
            return lights

        for light_id in self._list_light_ids():
            if self.is_reachable(light_id):
                lights.append(self._bridge[light_id])

        return lights

    def is_reachable(self, light_id):
        state = self._lights_refresh_state
        if light_id in state and \
           time.time() - state[light_id][0] < self.refresh_interval:
            return state[light_id][1]
        else:
            reachable = self._bridge[light_id].reachable
            state[light_id] = (time.time(), reachable)
            return reachable

    def get_light_objects(self):
        return self._get_reachable()

    def get_light_ids(self):
        out = []
        for light in self._get_reachable():
            out.append(light.light_id)
        return(out)


class ReachableLightsFactory(object):

    """Helper class to generate multiple reachable light objects. Useful in
    scripts which control different rooms.

    :param bridge: The bridge object.
    :type bridge: lively_lights.phue.Bridge

    :param day_night: A DayNight object.
    :type day_night: lively_lights.DayNight

    :param int refresh_interval: Search every n seconds for new lights.

    """

    def __init__(self, bridge, day_night, refresh_interval=60):
        self._bridge = bridge
        self._day_night = day_night
        self._refresh_interval = refresh_interval

    def get_lights(self, *light_ids):
        """
        :param list light_ids: Light IDs to filter the output of the methods
          :class:`lively_lights.ReachableLights.get_light_objects` and
          :class:`lively_lights.ReachableLights.get_light_ids`.
        """
        return ReachableLights(self._bridge, self._day_night, light_ids,
                               self._refresh_interval)
