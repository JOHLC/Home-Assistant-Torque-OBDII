"""Tests for Torque OBD-II helper functions."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.torque_obd import _extract_name_from_value, _normalize_pid
from custom_components.torque_obd.const import DOMAIN, SENSOR_DEFINITIONS
from custom_components.torque_obd.sensor import (
    _build_lookup_keys,
    _build_sensor_definition,
    _migrate_entity_registry_names,
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


@pytest.mark.parametrize(
    ("vehicle_name", "restored_name", "expected_name"),
    [
        # Exact case match
        ("Family Car", "Family Car Cruise Speed", "Cruise Speed"),
        # Lowercase vehicle name prefix in restored_name
        ("Family Car", "family car Cruise Speed", "Cruise Speed"),
        # Uppercase vehicle name prefix in restored_name
        ("Family Car", "FAMILY CAR Cruise Speed", "Cruise Speed"),
        # Vehicle name itself is lowercase
        ("family car", "Family Car Cruise Speed", "Cruise Speed"),
        # Mixed case vehicle name and restored name
        ("2025 Ford Escape", "2025 ford escape Vehicle Speed", "Vehicle Speed"),
        # No vehicle prefix – name is kept as-is
        ("Family Car", "Cruise Speed", "Cruise Speed"),
        # Leading/trailing whitespace on vehicle_name is ignored
        ("  Family Car  ", "Family Car Cruise Speed", "Cruise Speed"),
    ],
)
def test_build_sensor_definition_strips_vehicle_prefix_robustly(
    vehicle_name: str, restored_name: str, expected_name: str
) -> None:
    """Vehicle prefix stripping should be case-insensitive and whitespace-tolerant."""
    definition = _build_sensor_definition(
        SENSOR_DEFINITIONS,
        "kd",
        vehicle_name,
        restored_name,
    )
    assert definition["name"] == expected_name


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


# ---------------------------------------------------------------------------
# _migrate_entity_registry_names tests
# ---------------------------------------------------------------------------

def _make_registry_entry(
    entity_id: str,
    unique_id: str,
    original_name: str | None = None,
    name: str | None = None,
    disabled_by: object = None,
) -> MagicMock:
    """Create a minimal RegistryEntry-like mock."""
    entry = MagicMock()
    entry.entity_id = entity_id
    entry.unique_id = unique_id
    entry.original_name = original_name
    entry.name = name
    entry.disabled_by = disabled_by
    return entry


def _make_registry(existing_ids: set[str] | None = None) -> MagicMock:
    """Create a minimal EntityRegistry mock."""
    registry = MagicMock()
    existing_ids = existing_ids or set()

    def _async_get(entity_id: str):
        return MagicMock() if entity_id in existing_ids else None

    registry.async_get.side_effect = _async_get
    return registry


def test_migrate_entity_registry_names_strips_prefix_and_renames_entity_id() -> None:
    """Entries whose original_name starts with the vehicle prefix are migrated."""
    entry_id = "abc123"
    unique_id_prefix = f"{DOMAIN}_{entry_id}_"
    skipped = {f"{unique_id_prefix}api_endpoint", f"{unique_id_prefix}last_torque_update"}
    vehicle_name = "2025 Ford Escape"

    entries = [
        _make_registry_entry(
            entity_id="sensor.2025_ford_escape_2025_ford_escape_fuel_level",
            unique_id=f"{unique_id_prefix}k2f",
            original_name="2025 Ford Escape Fuel Level",
        ),
        _make_registry_entry(
            entity_id="sensor.2025_ford_escape_2025_ford_escape_engine_rpm",
            unique_id=f"{unique_id_prefix}k0c",
            original_name="2025 Ford Escape Engine RPM",
        ),
    ]

    registry = _make_registry()
    count = _migrate_entity_registry_names(
        registry, entries, unique_id_prefix, skipped, vehicle_name
    )

    assert count == 2
    assert registry.async_update_entity.call_count == 2
    registry.async_update_entity.assert_any_call(
        "sensor.2025_ford_escape_2025_ford_escape_fuel_level",
        original_name="Fuel Level",
        new_entity_id="sensor.2025_ford_escape_fuel_level",
    )
    registry.async_update_entity.assert_any_call(
        "sensor.2025_ford_escape_2025_ford_escape_engine_rpm",
        original_name="Engine RPM",
        new_entity_id="sensor.2025_ford_escape_engine_rpm",
    )


def test_migrate_entity_registry_names_skips_already_correct_entries() -> None:
    """Entries whose original_name has no vehicle prefix are left untouched."""
    entry_id = "abc123"
    unique_id_prefix = f"{DOMAIN}_{entry_id}_"
    skipped: set[str] = set()
    vehicle_name = "Family Car"

    entries = [
        _make_registry_entry(
            entity_id="sensor.family_car_fuel_level",
            unique_id=f"{unique_id_prefix}k2f",
            original_name="Fuel Level",  # Already correct — no prefix
        ),
    ]

    registry = _make_registry()
    count = _migrate_entity_registry_names(
        registry, entries, unique_id_prefix, skipped, vehicle_name
    )

    assert count == 0
    registry.async_update_entity.assert_not_called()


def test_migrate_entity_registry_names_skips_none_original_name() -> None:
    """Entries without an original_name are skipped safely."""
    entry_id = "abc123"
    unique_id_prefix = f"{DOMAIN}_{entry_id}_"
    vehicle_name = "Family Car"

    entries = [
        _make_registry_entry(
            entity_id="sensor.family_car_something",
            unique_id=f"{unique_id_prefix}k0c",
            original_name=None,
        ),
    ]

    registry = _make_registry()
    count = _migrate_entity_registry_names(
        registry, entries, unique_id_prefix, set(), vehicle_name
    )

    assert count == 0
    registry.async_update_entity.assert_not_called()


def test_migrate_entity_registry_names_skips_special_entries() -> None:
    """api_endpoint and last_torque_update entries are never touched."""
    entry_id = "abc123"
    unique_id_prefix = f"{DOMAIN}_{entry_id}_"
    skipped = {f"{unique_id_prefix}api_endpoint", f"{unique_id_prefix}last_torque_update"}
    vehicle_name = "My Car"

    entries = [
        _make_registry_entry(
            entity_id="sensor.my_car_api_endpoint",
            unique_id=f"{unique_id_prefix}api_endpoint",
            original_name="My Car API Endpoint",
        ),
        _make_registry_entry(
            entity_id="sensor.my_car_last_torque_update",
            unique_id=f"{unique_id_prefix}last_torque_update",
            original_name="My Car Last Torque Update",
        ),
    ]

    registry = _make_registry()
    count = _migrate_entity_registry_names(
        registry, entries, unique_id_prefix, skipped, vehicle_name
    )

    assert count == 0
    registry.async_update_entity.assert_not_called()


def test_migrate_entity_registry_names_case_insensitive_prefix_match() -> None:
    """Vehicle prefix stripping is case-insensitive."""
    entry_id = "abc123"
    unique_id_prefix = f"{DOMAIN}_{entry_id}_"
    vehicle_name = "Family Car"

    entries = [
        _make_registry_entry(
            entity_id="sensor.family_car_family_car_speed",
            unique_id=f"{unique_id_prefix}k0d",
            original_name="FAMILY CAR Speed",  # Upper-case prefix
        ),
    ]

    registry = _make_registry()
    count = _migrate_entity_registry_names(
        registry, entries, unique_id_prefix, set(), vehicle_name
    )

    assert count == 1
    registry.async_update_entity.assert_called_once_with(
        "sensor.family_car_family_car_speed",
        original_name="Speed",
        new_entity_id="sensor.family_car_speed",
    )


def test_migrate_entity_registry_names_skips_entity_id_rename_when_target_taken() -> None:
    """If the expected entity_id is occupied by a different entity, only original_name is fixed."""
    entry_id = "abc123"
    unique_id_prefix = f"{DOMAIN}_{entry_id}_"
    vehicle_name = "My Car"

    entries = [
        _make_registry_entry(
            entity_id="sensor.my_car_my_car_speed",
            unique_id=f"{unique_id_prefix}k0d",
            original_name="My Car Speed",
        ),
    ]

    # Target entity_id is already occupied by a *different* entity
    registry = _make_registry(existing_ids={"sensor.my_car_speed"})
    # Make the existing entity have a different unique_id
    existing_mock = MagicMock()
    existing_mock.unique_id = "completely_different_uid"
    registry.async_get.return_value = existing_mock

    count = _migrate_entity_registry_names(
        registry, entries, unique_id_prefix, set(), vehicle_name
    )

    assert count == 1
    # Only original_name is updated — no new_entity_id
    registry.async_update_entity.assert_called_once_with(
        "sensor.my_car_my_car_speed",
        original_name="Speed",
    )


def test_migrate_entity_registry_names_is_idempotent() -> None:
    """Running the migration twice does not change already-migrated entries."""
    entry_id = "abc123"
    unique_id_prefix = f"{DOMAIN}_{entry_id}_"
    vehicle_name = "Family Car"

    # Entry that has already been migrated (original_name has no vehicle prefix)
    entries = [
        _make_registry_entry(
            entity_id="sensor.family_car_fuel_level",
            unique_id=f"{unique_id_prefix}k2f",
            original_name="Fuel Level",
        ),
    ]

    registry = _make_registry()
    count = _migrate_entity_registry_names(
        registry, entries, unique_id_prefix, set(), vehicle_name
    )

    assert count == 0
    registry.async_update_entity.assert_not_called()


def test_migrate_entity_registry_names_fixes_entity_id_when_name_already_stripped() -> None:
    """Case B: entity_id still has double prefix even though original_name is already correct.

    This happens when a prior code change caused HA's async_get_or_create to
    update original_name in the registry to the stripped value, but the entity_id
    was never corrected.  The migration should rename only the entity_id.
    """
    entry_id = "abc123"
    unique_id_prefix = f"{DOMAIN}_{entry_id}_"
    vehicle_name = "2025 Ford Escape"

    entries = [
        _make_registry_entry(
            entity_id="sensor.2025_ford_escape_2025_ford_escape_fuel_level",
            unique_id=f"{unique_id_prefix}k2f",
            original_name="Fuel Level",  # already correct — no vehicle prefix
        ),
        _make_registry_entry(
            entity_id="sensor.2025_ford_escape_2025_ford_escape_engine_rpm",
            unique_id=f"{unique_id_prefix}k0c",
            original_name="Engine RPM",  # already correct — no vehicle prefix
        ),
    ]

    registry = _make_registry()
    count = _migrate_entity_registry_names(
        registry, entries, unique_id_prefix, set(), vehicle_name
    )

    assert count == 2
    assert registry.async_update_entity.call_count == 2
    # Only new_entity_id should be updated — original_name is already correct
    registry.async_update_entity.assert_any_call(
        "sensor.2025_ford_escape_2025_ford_escape_fuel_level",
        new_entity_id="sensor.2025_ford_escape_fuel_level",
    )
    registry.async_update_entity.assert_any_call(
        "sensor.2025_ford_escape_2025_ford_escape_engine_rpm",
        new_entity_id="sensor.2025_ford_escape_engine_rpm",
    )


def test_migrate_entity_registry_names_handles_static_sensors() -> None:
    """Static sensors (api_endpoint, last_torque_update) are migrated when not skipped.

    When async_setup_entry passes an empty set as skipped_unique_ids, static
    sensors that carry a double-prefix entity_id are also corrected.
    """
    entry_id = "abc123"
    unique_id_prefix = f"{DOMAIN}_{entry_id}_"
    vehicle_name = "2025 Ford Escape"

    entries = [
        _make_registry_entry(
            entity_id="sensor.2025_ford_escape_2025_ford_escape_api_endpoint",
            unique_id=f"{unique_id_prefix}api_endpoint",
            original_name="API Endpoint",  # already correct
        ),
        _make_registry_entry(
            entity_id="sensor.2025_ford_escape_2025_ford_escape_last_torque_update",
            unique_id=f"{unique_id_prefix}last_torque_update",
            original_name="Last Torque Update",  # already correct
        ),
    ]

    registry = _make_registry()
    # Pass empty set — static sensors should NOT be skipped from migration
    count = _migrate_entity_registry_names(
        registry, entries, unique_id_prefix, set(), vehicle_name
    )

    assert count == 2
    registry.async_update_entity.assert_any_call(
        "sensor.2025_ford_escape_2025_ford_escape_api_endpoint",
        new_entity_id="sensor.2025_ford_escape_api_endpoint",
    )
    registry.async_update_entity.assert_any_call(
        "sensor.2025_ford_escape_2025_ford_escape_last_torque_update",
        new_entity_id="sensor.2025_ford_escape_last_torque_update",
    )
