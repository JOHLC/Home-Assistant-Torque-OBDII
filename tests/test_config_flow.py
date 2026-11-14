"""Tests for the Torque OBD-II config flow helpers."""

from __future__ import annotations

import asyncio
from hashlib import sha256
from types import SimpleNamespace

import pytest

from custom_components.torque_obd.config_flow import TorqueConfigFlow, validate_input
from custom_components.torque_obd.const import CONF_EMAIL, CONF_UPLOAD_TOKEN_HASH, CONF_VEHICLE_NAME


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


@pytest.mark.parametrize(
    ("user_input", "expected_hash", "error"),
    [
        ({}, "previous-hash", None),
        ({"disable_upload_auth": True}, None, None),
        ({"upload_token": "new-upload-token"}, sha256(b"new-upload-token").hexdigest(), None),
        ({"upload_token": "bad token"}, None, "invalid_upload_token"),
        ({"upload_token": "a" * 1025}, None, "invalid_upload_token"),
        (
            {"upload_token": "new-upload-token", "disable_upload_auth": True},
            None,
            "conflicting_upload_auth_options",
        ),
    ],
)
def test_upload_auth_options(user_input, expected_hash, error):
    """The options flow preserves, rotates, or explicitly clears the token hash."""
    entry = SimpleNamespace(options={CONF_UPLOAD_TOKEN_HASH: "previous-hash", "other": 42})
    flow = TorqueConfigFlow.async_get_options_flow(entry)
    flow.handler = "vehicle"
    flow.hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_get_known_entry=lambda _: entry)
    )
    result = asyncio.run(flow.async_step_init(user_input))

    if error:
        assert error in result["errors"].values()
        return

    expected_options = {"other": 42}
    if expected_hash:
        expected_options[CONF_UPLOAD_TOKEN_HASH] = expected_hash
    assert result["data"] == expected_options


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("user_input", [None, {"upload_token": "bad token"}])
def test_upload_auth_form_only_offers_disable_when_enabled(enabled, user_input):
    """Only show the disable field when the vehicle has a token hash."""
    entry = SimpleNamespace(
        options={CONF_UPLOAD_TOKEN_HASH: "previous-hash"} if enabled else {}
    )
    flow = TorqueConfigFlow.async_get_options_flow(entry)
    flow.handler = "vehicle"
    flow.hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_get_known_entry=lambda _: entry)
    )

    result = asyncio.run(flow.async_step_init(user_input))

    assert "upload_token" in result["data_schema"].schema
    assert ("disable_upload_auth" in result["data_schema"].schema) is enabled
    assert result["description_placeholders"]["status"] == (
        "enabled" if enabled else "disabled"
    )
