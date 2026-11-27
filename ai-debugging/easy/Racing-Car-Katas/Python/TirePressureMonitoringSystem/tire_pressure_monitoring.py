from sensor import Sensor
from collections import deque

class Alarm(object):

    def __init__(self, sensor=None):
        """Initialize thresholds and the off alarm state, using the supplied sensor or a default Sensor."""
        self._low_pressure_threshold = 17
        self._high_pressure_threshold = 21
        self._extreme_low_pressure_threshold = 15
        self._extreme_high_pressure_threshold = 23
        self._sensor = sensor if sensor is not None else Sensor()
        self._is_alarm_on = False
        self._reading_history = deque()
        
    def check(self):
        """Read pressure, immediately latch extreme readings, and debounce other out-of-range readings."""
        psi_pressure_value = self._sensor.pop_next_pressure_psi_value()
        if self._is_alarm_on:
            self.update_reading_history(psi_pressure_value)
            return
        if self.should_trigger_alarm_for_extreme_pressure(psi_pressure_value):
            self._is_alarm_on = True
        elif self.should_trigger_alarm_for_pressure_drop(psi_pressure_value):
            self._is_alarm_on = True
        elif self.should_trigger_alarm_for_minor_pressure(psi_pressure_value):
            self._is_alarm_on = True
        self.update_reading_history(psi_pressure_value)

    def update_reading_history(self, pressure, max_len=3):
        """Append a pressure reading and discard the oldest if the history exceeds max_len."""
        self._reading_history.append(pressure)
        if len(self._reading_history) > max_len:
            self._reading_history.popleft()

    def should_trigger_alarm_for_extreme_pressure(self, pressure):
        """Return True only when pressure is strictly below 15 PSI or above 23 PSI."""
        return pressure < self._extreme_low_pressure_threshold \
            or pressure > self._extreme_high_pressure_threshold

    def should_trigger_alarm_for_pressure_drop(self, pressure):
        """Return True when pressure is at least 3 PSI below either of the two previous readings."""
        if len(self._reading_history) < 2:
            return False
        return any(
            pressure <= previous_pressure - 3.0
            for previous_pressure in (self._reading_history[-2], self._reading_history[-1])
        )

    def should_trigger_alarm_for_minor_pressure(self, pressure):
        """Return True when the previous and current readings are both outside the normal range."""
        return (
            bool(self._reading_history)
            and not self.is_normal_range(self._reading_history[-1])
            and not self.is_normal_range(pressure)
        )

    def is_normal_range(self, pressure):
        """Return True when pressure is inclusively between 17 and 21 PSI."""
        return self._low_pressure_threshold <= pressure <= self._high_pressure_threshold

    def reset(self):
        """Clear the latched alarm and all recorded tire-pressure readings."""
        self._is_alarm_on = False
        self._reading_history.clear()

    @property
    def is_alarm_on(self):
        """Return whether the alarm is currently on."""
        return self._is_alarm_on
