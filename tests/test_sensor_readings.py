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
