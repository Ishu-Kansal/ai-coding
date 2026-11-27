import unittest

from sensor import Sensor
from tire_pressure_monitoring import Alarm

class AlarmTest(unittest.TestCase):

    def test_alarm_is_off_by_default(self):
        alarm = Alarm()
        assert not alarm.is_alarm_on

    def test_alarm_is_off_for_single_minor_pressure_reading(self):
        alarm = Alarm(Sensor(deterministic_value=0))
        alarm.check()
        assert alarm.is_alarm_on is False

    def test_first_reading_of_16_psi_does_not_trigger_alarm(self):
        alarm = Alarm(Sensor(deterministic_value=0))
        alarm.check()
        self.assertEqual(alarm._reading_history[-1], 16)
        self.assertFalse(alarm.is_alarm_on)

    def test_alarm_is_on_ten_above_offset(self):
        alarm = Alarm(Sensor(deterministic_value=10))
        alarm.check()
        assert alarm.is_alarm_on is True

    def test_alarm_stays_on_until_reset(self):
        sensor = Sensor(deterministic_value=0)
        alarm = Alarm(sensor)
        alarm.check()
        assert alarm.is_alarm_on is False
        alarm.check()
        assert alarm.is_alarm_on is True

        sensor.deterministic_value = 0.9
        alarm.check()
        assert alarm.is_alarm_on is True

        alarm.reset()
        assert alarm.is_alarm_on is False

        alarm.check()
        assert alarm.is_alarm_on is False

    def test_reset_clears_history_before_next_minor_reading(self):
        sensor = Sensor(deterministic_value=0.5)
        alarm = Alarm(sensor)
        alarm.check()

        sensor.deterministic_value = 0.8
        alarm.check()
        alarm.reset()

        sensor.deterministic_value = 0.1
        alarm.check()

        self.assertFalse(alarm.is_alarm_on)
        self.assertEqual(list(alarm._reading_history), [16.1])

    def test_two_consecutive_minor_out_of_range_readings_trigger_alarm(self):
        for pressure_variation in (-1.0, 0.9, 5.1, 7.0):
            with self.subTest(pressure_variation=pressure_variation):
                alarm = Alarm(Sensor(deterministic_value=pressure_variation))
                alarm.check()
                self.assertFalse(alarm.is_alarm_on)
                alarm.check()
                self.assertTrue(alarm.is_alarm_on)

    def test_three_readings_21_20_19_do_not_trigger_drop_alarm(self):
        sensor = Sensor()
        alarm = Alarm(sensor)
        for pressure_variation in (5, 4, 3):
            sensor.deterministic_value = pressure_variation
            alarm.check()

        self.assertEqual(list(alarm._reading_history), [21, 20, 19])
        self.assertFalse(alarm.is_alarm_on)

    def test_three_readings_21_20_17_trigger_drop_alarm(self):
        sensor = Sensor()
        alarm = Alarm(sensor)
        for pressure_variation in (5, 4, 1):
            sensor.deterministic_value = pressure_variation
            alarm.check()

        self.assertEqual(list(alarm._reading_history), [21, 20, 17])
        self.assertTrue(alarm.is_alarm_on)

    def test_reading_history_keeps_only_the_latest_three_values(self):
        alarm = Alarm()
        for pressure in (17, 18, 19, 20):
            alarm.update_reading_history(pressure)

        self.assertEqual(list(alarm._reading_history), [18, 19, 20])

    def test_extreme_pressure_readings_latch_alarm(self):
        for pressure_variation in (-1.1, 7.1):
            with self.subTest(pressure_variation=pressure_variation):
                sensor = Sensor(deterministic_value=pressure_variation)
                alarm = Alarm(sensor)

                alarm.check()
                self.assertTrue(alarm.is_alarm_on)

                sensor.deterministic_value = 2
                alarm.check()
                self.assertTrue(alarm.is_alarm_on)

    def test_extreme_pressure_predicate_uses_strict_bounds(self):
        alarm = Alarm()
        for pressure, expected in (
            (14.9, True),
            (15.0, False),
            (23.0, False),
            (23.1, True),
        ):
            with self.subTest(pressure=pressure):
                self.assertEqual(
                    alarm.should_trigger_alarm_for_extreme_pressure(pressure),
                    expected,
                )