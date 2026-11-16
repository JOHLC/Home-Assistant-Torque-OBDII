"""Regression tests for Torque temperature readings and GPS bearing names."""

from unittest.mock import MagicMock

import pytest

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTemperature

from custom_components.torque_obd.sensor import TorqueSensor


@pytest.mark.parametrize("pid", ["k5", "k0f", "k46"])
def test_standard_temperature_rejects_corrupted_readings(pid):
    sensor = TorqueSensor(
        MagicMock(), "entry", "", "Car", pid,
        {
            "name": "Temperature",
            "unit": UnitOfTemperature.CELSIUS,
            "device_class": SensorDeviceClass.TEMPERATURE,
        },
    )
    sensor.async_write_ha_state = MagicMock()

    sensor._handle_update({pid: "1.429e25"})
    assert sensor.native_value is None

    sensor._handle_update({pid: "20"})
    assert sensor.native_value == 20
    assert sensor._parse_value("68", UnitOfTemperature.FAHRENHEIT) == pytest.approx(20)


@pytest.mark.parametrize(
    ("pid", "expected"), [("kff1007", "GPS Bearing"), ("kff123b", "GPS Bearing (alternate)")]
)
def test_gps_bearings_have_distinct_names_and_preserve_identity(pid, expected):
    sensor = TorqueSensor(MagicMock(), "entry", "", "Car", pid, {"name": "GPS Bearing"})
    assert sensor.name == expected
    assert sensor.unique_id == f"torque_obd_entry_{pid}"


def test_sensors_sharing_pid_update_from_indexed_readings_and_units():
    payload = {
        "k220104": "12.5",
        "k220104__1": "48.0",
    }
    brake_pressure = TorqueSensor(
        MagicMock(), "entry", "", "Car", "k220104", {"name": "Brake Pressure"}
    )
    abs_speed = TorqueSensor(
        MagicMock(), "entry", "", "Car", "k220104__1", {"name": "ABS Speed"}
    )
    brake_pressure.async_write_ha_state = MagicMock()
    abs_speed.async_write_ha_state = MagicMock()

    brake_pressure._handle_update(payload)
    abs_speed._handle_update(payload)

    assert brake_pressure.native_value == 12.5
    assert abs_speed.native_value == 48.0
