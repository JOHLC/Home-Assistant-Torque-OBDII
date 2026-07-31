"""Tests for the Torque OBD-II GPS device tracker."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.torque_obd.const import (
    DOMAIN,
    GPS_ACCURACY_PID,
    GPS_ALTITUDE_PID,
    GPS_BEARING_PID,
    GPS_LATITUDE_PID,
    GPS_LONGITUDE_PID,
    GPS_SPEED_PID,
)
from custom_components.torque_obd.device_tracker import (
    TRACKER_UNIQUE_ID_SUFFIX,
    TorqueDeviceTracker,
)


# ---------------------------------------------------------------------------
# Constants used across tests
# ---------------------------------------------------------------------------

ENTRY_ID = "test_entry_abc"
VEHICLE_NAME = "2025 Ford Escape"
UNIQUE_ID = f"{DOMAIN}_{ENTRY_ID}_{TRACKER_UNIQUE_ID_SUFFIX}"

# Sample GPS payload matching real Torque payloads (from example-payload-data.md)
SAMPLE_GPS_PAYLOAD: dict[str, str] = {
    GPS_LATITUDE_PID: "42.123027155175805",
    GPS_LONGITUDE_PID: "-77.92161114513874",
    GPS_BEARING_PID: "294.8999938964844",
    GPS_ACCURACY_PID: "5.0",
    GPS_ALTITUDE_PID: "300.0",
    GPS_SPEED_PID: "0.107999994724989",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tracker(
    hass: MagicMock | None = None,
    entry_id: str = ENTRY_ID,
    vehicle_name: str = VEHICLE_NAME,
) -> TorqueDeviceTracker:
    """Create a TorqueDeviceTracker with an optional mock hass."""
    if hass is None:
        hass = MagicMock()
    return TorqueDeviceTracker(hass, entry_id, vehicle_name)


# ---------------------------------------------------------------------------
# GPS PID constant checks
# ---------------------------------------------------------------------------


def test_gps_pid_constants_defined() -> None:
    """GPS PID constants should be present and non-empty strings."""
    assert GPS_LATITUDE_PID == "kff1006"
    assert GPS_LONGITUDE_PID == "kff1005"
    assert GPS_ACCURACY_PID == "kff1239"
    assert GPS_BEARING_PID == "kff1007"
    assert GPS_ALTITUDE_PID == "kff1010"
    assert GPS_SPEED_PID == "kff1001"


# ---------------------------------------------------------------------------
# TorqueDeviceTracker initialisation
# ---------------------------------------------------------------------------


def test_tracker_initialises_correctly() -> None:
    """Tracker should initialise with the expected name and unique_id."""
    tracker = _make_tracker()

    assert tracker._attr_name == VEHICLE_NAME
    assert tracker._attr_unique_id == UNIQUE_ID
    assert tracker._attr_latitude is None
    assert tracker._attr_longitude is None
    assert tracker._attr_location_accuracy == 0


def test_tracker_unique_id_is_per_entry() -> None:
    """Each config entry produces a distinct unique_id."""
    tracker_a = _make_tracker(entry_id="entry_1")
    tracker_b = _make_tracker(entry_id="entry_2")

    assert tracker_a._attr_unique_id != tracker_b._attr_unique_id
    assert "entry_1" in tracker_a._attr_unique_id
    assert "entry_2" in tracker_b._attr_unique_id


def test_tracker_source_type_is_gps() -> None:
    """Source type should always be GPS."""
    from homeassistant.components.device_tracker import SourceType

    tracker = _make_tracker()
    assert tracker._attr_source_type == SourceType.GPS


def test_tracker_entity_category_is_none() -> None:
    """Entity category must not be DIAGNOSTIC so the tracker is a primary entity."""
    tracker = _make_tracker()
    assert tracker._attr_entity_category is None


# ---------------------------------------------------------------------------
# _handle_update – normal GPS data
# ---------------------------------------------------------------------------


def test_handle_update_sets_lat_lon() -> None:
    """A payload with lat/lon should update the tracker coordinates."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()

    tracker._handle_update(SAMPLE_GPS_PAYLOAD)

    assert tracker._attr_latitude == pytest.approx(42.123027155175805)
    assert tracker._attr_longitude == pytest.approx(-77.92161114513874)
    tracker.async_write_ha_state.assert_called_once()


def test_handle_update_sets_accuracy() -> None:
    """A payload with GPS accuracy should update location_accuracy."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()

    tracker._handle_update(SAMPLE_GPS_PAYLOAD)

    assert tracker._attr_location_accuracy == pytest.approx(5.0)


def test_handle_update_sets_extra_attributes() -> None:
    """Bearing, altitude and speed should be stored as extra state attributes."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()

    tracker._handle_update(SAMPLE_GPS_PAYLOAD)

    attrs = tracker._attr_extra_state_attributes
    assert attrs["bearing"] == pytest.approx(294.8999938964844)
    assert attrs["altitude"] == pytest.approx(300.0)
    assert attrs["speed"] == pytest.approx(0.107999994724989)


# ---------------------------------------------------------------------------
# _handle_update – missing or partial GPS data
# ---------------------------------------------------------------------------


def test_handle_update_skips_when_no_lat() -> None:
    """Payload missing latitude should not change the tracker coordinates."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()

    payload_no_lat = {GPS_LONGITUDE_PID: "-77.0"}
    tracker._handle_update(payload_no_lat)

    assert tracker._attr_latitude is None
    assert tracker._attr_longitude is None
    tracker.async_write_ha_state.assert_not_called()


def test_handle_update_skips_when_no_lon() -> None:
    """Payload missing longitude should not change the tracker coordinates."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()

    payload_no_lon = {GPS_LATITUDE_PID: "42.0"}
    tracker._handle_update(payload_no_lon)

    assert tracker._attr_latitude is None
    assert tracker._attr_longitude is None
    tracker.async_write_ha_state.assert_not_called()


def test_handle_update_skips_when_gps_absent_from_payload() -> None:
    """A payload with no GPS keys at all should not change the tracker."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()
    tracker._attr_latitude = 42.0
    tracker._attr_longitude = -77.0

    tracker._handle_update({"kd": "50.0", "k0c": "3200.0"})

    # Previous coordinates preserved
    assert tracker._attr_latitude == pytest.approx(42.0)
    assert tracker._attr_longitude == pytest.approx(-77.0)
    tracker.async_write_ha_state.assert_not_called()


def test_handle_update_handles_invalid_lat() -> None:
    """Invalid (non-numeric) latitude should not update coordinates."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()

    tracker._handle_update({GPS_LATITUDE_PID: "not-a-number", GPS_LONGITUDE_PID: "-77.0"})

    assert tracker._attr_latitude is None
    tracker.async_write_ha_state.assert_not_called()


def test_handle_update_handles_invalid_lon() -> None:
    """Invalid (non-numeric) longitude should not update coordinates."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()

    tracker._handle_update({GPS_LATITUDE_PID: "42.0", GPS_LONGITUDE_PID: "bad"})

    assert tracker._attr_longitude is None
    tracker.async_write_ha_state.assert_not_called()


def test_handle_update_tolerates_missing_optional_pids() -> None:
    """Payload with only lat/lon (no accuracy, bearing, altitude, speed) should work."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()

    minimal_payload = {GPS_LATITUDE_PID: "42.0", GPS_LONGITUDE_PID: "-77.0"}
    tracker._handle_update(minimal_payload)

    assert tracker._attr_latitude == pytest.approx(42.0)
    assert tracker._attr_longitude == pytest.approx(-77.0)
    assert tracker._attr_location_accuracy == 0  # unchanged default
    assert tracker._attr_extra_state_attributes == {}
    tracker.async_write_ha_state.assert_called_once()


def test_handle_update_tolerates_invalid_optional_pids() -> None:
    """Invalid optional PIDs should be silently skipped."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()

    payload = {
        GPS_LATITUDE_PID: "42.0",
        GPS_LONGITUDE_PID: "-77.0",
        GPS_ACCURACY_PID: "bad",
        GPS_BEARING_PID: "also-bad",
    }
    tracker._handle_update(payload)

    assert tracker._attr_latitude == pytest.approx(42.0)
    assert tracker._attr_location_accuracy == 0  # unchanged
    assert "bearing" not in tracker._attr_extra_state_attributes
    tracker.async_write_ha_state.assert_called_once()


# ---------------------------------------------------------------------------
# async_added_to_hass – state restoration
# ---------------------------------------------------------------------------


def test_async_added_to_hass_restores_coordinates() -> None:
    """On startup, last lat/lon from RestoreEntity should be applied."""
    from homeassistant.const import ATTR_GPS_ACCURACY, ATTR_LATITUDE, ATTR_LONGITUDE

    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()
    tracker.async_on_remove = MagicMock()

    # Build a mock last_state with GPS coordinates in attributes
    last_state = MagicMock()
    last_state.attributes = {
        ATTR_LATITUDE: 42.5,
        ATTR_LONGITUDE: -77.5,
        ATTR_GPS_ACCURACY: 8.0,
        "bearing": 120.0,
        "altitude": 250.0,
    }

    async def _run() -> None:
        with patch.object(
            tracker, "async_get_last_state", new=AsyncMock(return_value=last_state)
        ):
            await tracker.async_added_to_hass()

    asyncio.run(_run())

    assert tracker._attr_latitude == pytest.approx(42.5)
    assert tracker._attr_longitude == pytest.approx(-77.5)
    assert tracker._attr_location_accuracy == pytest.approx(8.0)
    assert tracker._attr_extra_state_attributes["bearing"] == pytest.approx(120.0)
    assert tracker._attr_extra_state_attributes["altitude"] == pytest.approx(250.0)
    tracker.async_write_ha_state.assert_called()


def test_async_added_to_hass_no_previous_state() -> None:
    """When there is no previous state, coordinates remain None."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()
    tracker.async_on_remove = MagicMock()

    async def _run() -> None:
        with patch.object(
            tracker, "async_get_last_state", new=AsyncMock(return_value=None)
        ):
            await tracker.async_added_to_hass()

    asyncio.run(_run())

    assert tracker._attr_latitude is None
    assert tracker._attr_longitude is None
    tracker.async_write_ha_state.assert_not_called()


def test_async_added_to_hass_subscribes_to_dispatcher() -> None:
    """async_added_to_hass should subscribe to the domain update signal."""
    tracker = _make_tracker()
    tracker.async_write_ha_state = MagicMock()
    tracker.async_on_remove = MagicMock()

    captured_signal: list[str] = []

    def _fake_dispatcher_connect(hass: object, signal: str, callback: object) -> object:
        captured_signal.append(signal)
        return MagicMock()

    async def _run() -> None:
        with (
            patch.object(
                tracker, "async_get_last_state", new=AsyncMock(return_value=None)
            ),
            patch(
                "custom_components.torque_obd.device_tracker.async_dispatcher_connect",
                side_effect=_fake_dispatcher_connect,
            ),
        ):
            await tracker.async_added_to_hass()

    asyncio.run(_run())

    assert len(captured_signal) == 1
    expected_signal = f"{DOMAIN}_{ENTRY_ID}_update"
    assert captured_signal[0] == expected_signal


# ---------------------------------------------------------------------------
# async_setup_entry – restore from entity registry
# ---------------------------------------------------------------------------


def test_async_setup_entry_restores_existing_tracker() -> None:
    """When a tracker entity exists in the registry, it should be restored."""
    import asyncio

    from custom_components.torque_obd.device_tracker import async_setup_entry

    entry_id = "entry_restore"
    vehicle_name = "Test Car"
    unique_id = f"{DOMAIN}_{entry_id}_{TRACKER_UNIQUE_ID_SUFFIX}"

    hass = MagicMock()
    hass.data = {
        DOMAIN: {
            entry_id: {
                "vehicle_name": vehicle_name,
            }
        }
    }

    config_entry = MagicMock()
    config_entry.entry_id = entry_id
    config_entry.data = {"vehicle_name": vehicle_name}

    added_entities: list[TorqueDeviceTracker] = []

    def _fake_add_entities(entities: list, update_before_add: bool = False) -> None:
        added_entities.extend(entities)

    # Mock entity registry to return an existing entity for our unique_id
    mock_registry = MagicMock()
    mock_registry.async_get_entity_id.return_value = "device_tracker.test_car"

    with patch(
        "custom_components.torque_obd.device_tracker.er.async_get",
        return_value=mock_registry,
    ):
        asyncio.run(async_setup_entry(hass, config_entry, _fake_add_entities))

    assert len(added_entities) == 1
    assert isinstance(added_entities[0], TorqueDeviceTracker)
    assert added_entities[0]._vehicle_name == vehicle_name
    assert hass.data[DOMAIN][entry_id]["tracker_added"] is True

    # Registry lookup must use the correct arguments
    mock_registry.async_get_entity_id.assert_called_once_with(
        "device_tracker", DOMAIN, unique_id
    )


def test_async_setup_entry_does_not_restore_when_not_registered() -> None:
    """When no tracker exists in the registry, async_add_entities is not called."""
    import asyncio

    from custom_components.torque_obd.device_tracker import async_setup_entry

    entry_id = "entry_new"
    vehicle_name = "New Car"

    hass = MagicMock()
    hass.data = {
        DOMAIN: {
            entry_id: {
                "vehicle_name": vehicle_name,
            }
        }
    }

    config_entry = MagicMock()
    config_entry.entry_id = entry_id
    config_entry.data = {"vehicle_name": vehicle_name}

    added_entities: list = []

    def _fake_add_entities(entities: list, update_before_add: bool = False) -> None:
        added_entities.extend(entities)

    # Entity registry returns None → no previous registration
    mock_registry = MagicMock()
    mock_registry.async_get_entity_id.return_value = None

    with patch(
        "custom_components.torque_obd.device_tracker.er.async_get",
        return_value=mock_registry,
    ):
        asyncio.run(async_setup_entry(hass, config_entry, _fake_add_entities))

    assert added_entities == []
    assert hass.data[DOMAIN][entry_id]["tracker_added"] is False
    assert hass.data[DOMAIN][entry_id]["async_add_tracker"] is _fake_add_entities


# ---------------------------------------------------------------------------
# Platform integration – tracker creation via __init__.py
# ---------------------------------------------------------------------------


def test_gps_platform_in_platforms_list() -> None:
    """PLATFORMS should include Platform.DEVICE_TRACKER."""
    from homeassistant.const import Platform

    from custom_components.torque_obd import PLATFORMS

    assert Platform.DEVICE_TRACKER in PLATFORMS
