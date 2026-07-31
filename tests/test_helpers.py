"""Tests for Torque OBD-II helper functions."""

from __future__ import annotations

import pytest

from custom_components.torque_obd import _extract_name_from_value, _normalize_pid
from custom_components.torque_obd.const import SENSOR_DEFINITIONS
from custom_components.torque_obd.sensor import (
    _build_lookup_keys,
    _build_sensor_definition,
)


@pytest.mark.parametrize(
    ("pid", "expected"),
    [
        ("k5", "k05"),
        ("kd", "k0d"),
        ("k0d", "k0d"),
        ("k221e1c", "k221e1c"),
        ("not-a-pid", "not-a-pid"),
    ],
)
def test_normalize_pid(pid: str, expected: str) -> None:
    """PID normalization should preserve aliases and extended PIDs."""
    assert _normalize_pid(pid) == expected


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("kd", ("kd", "k0d")),
        ("k0d", ("k0d", "kd")),
        ("k221e1c", ("k221e1c",)),
    ],
)
def test_build_lookup_keys(key: str, expected: tuple[str, ...]) -> None:
    """Lookup keys should include short and zero-padded standard PID aliases."""
    assert _build_lookup_keys(key) == expected


def test_extract_name_from_value_prefers_first_list_entry() -> None:
    """Name extraction should support both arrays and strings."""
    assert _extract_name_from_value(["Speed", "Vehicle Speed"]) == "Speed"
    assert _extract_name_from_value("Boost") == "Boost"
    assert _extract_name_from_value([]) is None


def test_build_sensor_definition_uses_restored_name_without_vehicle_prefix() -> None:
    """Restored entity names should override the default definition name."""
    definition = _build_sensor_definition(
        SENSOR_DEFINITIONS,
        "kd",
        "Family Car",
        "Family Car Cruise Speed",
    )

    assert definition["name"] == "Cruise Speed"
    assert definition["unit"] == SENSOR_DEFINITIONS["k0d"]["unit"]


def test_build_sensor_definition_falls_back_for_unknown_pid() -> None:
    """Unknown PIDs should get a generic fallback definition."""
    definition = _build_sensor_definition(SENSOR_DEFINITIONS, "k999", "Family Car")

    assert definition == {
        "name": "PID k999",
        "unit": None,
        "icon": "mdi:car-info",
        "device_class": None,
        "state_class": None,
    }
