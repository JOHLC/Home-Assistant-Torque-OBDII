"""Tests for the Torque OBD-II config flow helpers."""

from __future__ import annotations

import asyncio

import pytest

from custom_components.torque_obd.config_flow import validate_input
from custom_components.torque_obd.const import CONF_EMAIL, CONF_VEHICLE_NAME


def test_validate_input_accepts_stripped_vehicle_name() -> None:
    """Valid input should return a stripped config entry title."""
    result = asyncio.run(
        validate_input(
            None,
            {
                CONF_VEHICLE_NAME: "  Family Car  ",
                CONF_EMAIL: "driver@example.com",
            },
        )
    )

    assert result == {"title": "Family Car"}


@pytest.mark.parametrize(
    ("vehicle_name", "error_message"),
    [
        ("", "Vehicle name cannot be empty"),
        ("My/Car", "Vehicle name contains invalid characters"),
    ],
)
def test_validate_input_rejects_invalid_vehicle_names(
    vehicle_name: str,
    error_message: str,
) -> None:
    """Invalid vehicle names should raise a ValueError."""
    with pytest.raises(ValueError, match=error_message):
        asyncio.run(validate_input(None, {CONF_VEHICLE_NAME: vehicle_name}))


@pytest.mark.parametrize("email", ["driverexample.com", "driver@", "@example.com"])
def test_validate_input_rejects_invalid_email(email: str) -> None:
    """Invalid emails should raise a ValueError."""
    with pytest.raises(ValueError, match="Invalid email format"):
        asyncio.run(
            validate_input(
                None,
                {
                    CONF_VEHICLE_NAME: "Family Car",
                    CONF_EMAIL: email,
                },
            )
        )
