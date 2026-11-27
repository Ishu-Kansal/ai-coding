import random

class Sensor(object):

    # The reading of the pressure value from the sensor is simulated in this implementation.
    # Because the focus of the exercise is on the other class.

    _OFFSET = 16

    def __init__(self, deterministic_value=None):
        """Store an optional deterministic pressure variation, or use random sampling when none is supplied."""
        self.deterministic_value = deterministic_value

    @property
    def deterministic_value(self):
        """Return the configured deterministic pressure variation, if any."""
        return self._deterministic_value

    @deterministic_value.setter
    def deterministic_value(self, value):
        """Set the deterministic pressure variation used by future sensor readings."""
        self._deterministic_value = value
        
    def pop_next_pressure_psi_value(self):
        """Combine the configured deterministic variation or a simulated sample with the 16 PSI offset."""
        pressure_telemetry_value = self.sample_pressure()
        return Sensor._OFFSET + pressure_telemetry_value

    def sample_pressure(self):
        """Return the configured deterministic pressure variation, or generate a random variation between 0 and 6 PSI."""
        if self.deterministic_value is not None:
            return self.deterministic_value

        # placeholder implementation that simulate a real sensor in a real tire
        pressure_telemetry_value = 6 * random.random() * random.random()
        return pressure_telemetry_value
