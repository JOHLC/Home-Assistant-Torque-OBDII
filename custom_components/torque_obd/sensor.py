"""Support for Torque OBD-II sensors."""

from __future__ import annotations

from datetime import datetime
import logging
import math
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er, network
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from . import _normalize_pid
from .const import CONF_EMAIL, CONF_VEHICLE_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _build_lookup_keys(key: str) -> tuple[str, ...]:
    """Build supported payload keys for a sensor."""
    normalized_key = _normalize_pid(key)
    lookup_keys = [key]

    if normalized_key not in lookup_keys:
        lookup_keys.append(normalized_key)

    if normalized_key.startswith("k0") and len(normalized_key) == 3:
        short_key = f"k{normalized_key[2:]}"
        if short_key not in lookup_keys:
            lookup_keys.append(short_key)

    return tuple(lookup_keys)


def _build_sensor_definition(
    sensor_definitions: dict[str, dict[str, Any]],
    key: str,
    vehicle_name: str,
    restored_name: str | None = None,
) -> dict[str, Any]:
    """Build a sensor definition for a restored or dynamic sensor."""
    normalized_key = _normalize_pid(key)
    definition = sensor_definitions.get(normalized_key, {}).copy()

    if not definition:
        definition = {
            "name": f"PID {key}",
            "unit": None,
            "icon": "mdi:car-info",
            "device_class": None,
            "state_class": None,
        }

    if restored_name:
        vehicle_prefix = f"{vehicle_name} "
        if restored_name.startswith(vehicle_prefix):
            restored_name = restored_name[len(vehicle_prefix) :]
        definition["name"] = restored_name

    return definition


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Torque sensors based on a config entry."""
    email = config_entry.data.get(CONF_EMAIL, "")
    vehicle_name = config_entry.data[CONF_VEHICLE_NAME]

    _LOGGER.info("Setting up Torque sensor platform for vehicle '%s'", vehicle_name)

    sensor_definitions = hass.data.get(DOMAIN, {}).get("sensor_definitions", {})
    if not sensor_definitions:
        _LOGGER.warning(
            "Sensor definitions not found during sensor setup for %s. "
            "This is unexpected - definitions should be loaded in __init__.py",
            vehicle_name,
        )

    hass.data.setdefault(DOMAIN, {}).setdefault(config_entry.entry_id, {})
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    added_sensors = entry_data.get("added_sensors")
    if not isinstance(added_sensors, set):
        added_sensors = set(added_sensors or [])

    entry_data.update(
        {
            "async_add_entities": async_add_entities,
            "added_sensors": added_sensors,
            "email": email,
            "vehicle_name": vehicle_name,
        }
    )

    sensors: list[SensorEntity] = [
        TorqueAPIEndpointSensor(
            hass,
            config_entry.entry_id,
            vehicle_name,
        ),
        TorqueLastUpdateSensor(
            hass,
            config_entry.entry_id,
            vehicle_name,
        ),
    ]

    unique_id_prefix = f"{DOMAIN}_{config_entry.entry_id}_"
    skipped_unique_ids = {
        f"{unique_id_prefix}api_endpoint",
        f"{unique_id_prefix}last_torque_update",
    }
    entity_registry = er.async_get(hass)
    registry_entries = er.async_entries_for_config_entry(
        entity_registry,
        config_entry.entry_id,
    )

    restored_sensor_count = 0
    disabled_sensor_keys: set[str] = set()
    restored_normalized_keys: set[str] = set()

    for registry_entry in registry_entries:
        unique_id = registry_entry.unique_id
        if unique_id in skipped_unique_ids or not unique_id.startswith(unique_id_prefix):
            continue

        key = unique_id.removeprefix(unique_id_prefix)
        normalized_key = _normalize_pid(key)

        if registry_entry.disabled_by is not None:
            disabled_sensor_keys.update({key, normalized_key})
            continue

        if normalized_key in restored_normalized_keys:
            added_sensors.update({key, normalized_key})
            continue

        definition = _build_sensor_definition(
            sensor_definitions,
            key,
            vehicle_name,
            registry_entry.name or registry_entry.original_name,
        )

        sensors.append(
            TorqueSensor(
                hass,
                config_entry.entry_id,
                email,
                vehicle_name,
                key,
                definition,
            )
        )
        added_sensors.update({key, normalized_key})
        restored_normalized_keys.add(normalized_key)
        restored_sensor_count += 1
        _LOGGER.debug(
            "Restoring sensor '%s' (PID: %s, normalized: %s) for vehicle '%s'",
            definition["name"],
            key,
            normalized_key,
            vehicle_name,
        )

    added_sensors.update(disabled_sensor_keys)

    if restored_sensor_count:
        _LOGGER.info(
            "Restored %d Torque sensor(s) from the entity registry for vehicle '%s'",
            restored_sensor_count,
            vehicle_name,
        )

    async_add_entities(sensors, True)
    _LOGGER.debug(
        "Added %d total sensor(s) for vehicle '%s' during setup",
        len(sensors),
        vehicle_name,
    )


class TorqueSensor(RestoreEntity, SensorEntity):
    """Representation of a Torque OBD-II sensor."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        email: str,
        vehicle_name: str,
        key: str,
        definition: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._email = email
        self._vehicle_name = vehicle_name
        self._key = key
        self._lookup_keys = _build_lookup_keys(key)
        self._definition = definition

        self._attr_name = definition["name"]
        self._attr_native_unit_of_measurement = definition.get("unit")
        self._attr_icon = definition.get("icon")

        if definition.get("device_class"):
            self._attr_device_class = definition["device_class"]

        if definition.get("state_class"):
            self._attr_state_class = definition["state_class"]

        self._attr_suggested_display_precision = 2
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{key}"
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

        _LOGGER.debug(
            "Initialized sensor '%s' (PID: %s) for vehicle '%s'",
            self._attr_name,
            key,
            vehicle_name,
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Torque vehicle."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=self._vehicle_name,
            manufacturer="Torque",
            model="OBD-II",
        )

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        _LOGGER.debug(
            "Added sensor '%s' (PID: %s) for vehicle '%s' to Home Assistant",
            self._attr_name,
            self._key,
            self._vehicle_name,
        )

        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (
            None,
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
        ):
            _LOGGER.debug(
                "Restoring previous state for sensor '%s': %s",
                self._attr_name,
                last_state.state,
            )

            try:
                restored_value = float(last_state.state)
                if not math.isfinite(restored_value):
                    _LOGGER.debug(
                        "Sensor '%s' had non-finite restored state '%s', setting to None",
                        self._attr_name,
                        last_state.state,
                    )
                    self._attr_native_value = None
                else:
                    self._attr_native_value = restored_value
            except (ValueError, TypeError):
                self._attr_native_value = last_state.state

            if last_state.attributes:
                custom_attrs = {}
                if "last_update" in last_state.attributes:
                    custom_attrs["last_update"] = last_state.attributes["last_update"]
                if "session" in last_state.attributes:
                    custom_attrs["session"] = last_state.attributes["session"]
                if "device_id" in last_state.attributes:
                    custom_attrs["device_id"] = last_state.attributes["device_id"]

                if custom_attrs:
                    self._attr_extra_state_attributes = custom_attrs
                    _LOGGER.debug(
                        "Restored attributes for sensor '%s': %s",
                        self._attr_name,
                        self._attr_extra_state_attributes,
                    )

            self.async_write_ha_state()
            _LOGGER.debug(
                "Wrote restored state to Home Assistant for sensor '%s'",
                self._attr_name,
            )

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_{self._entry_id}_update",
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self, data: dict[str, Any]) -> None:
        """Handle updated data from Torque."""
        payload_key = next((key for key in self._lookup_keys if key in data), None)
        if payload_key is None:
            return

        value = data[payload_key]
        old_value = self._attr_native_value

        try:
            converted_value = float(value)
            if not math.isfinite(converted_value):
                _LOGGER.debug(
                    "Sensor '%s' received non-finite value '%s', setting to None",
                    self._attr_name,
                    value,
                )
                self._attr_native_value = None
            else:
                self._attr_native_value = converted_value
        except (ValueError, TypeError):
            self._attr_native_value = value

        if old_value != self._attr_native_value:
            _LOGGER.debug(
                "Sensor '%s' updated: %s -> %s",
                self._attr_name,
                old_value,
                self._attr_native_value,
            )

        self._attr_extra_state_attributes = {
            "last_update": dt_util.utcnow().isoformat(),
        }

        if "session" in data:
            self._attr_extra_state_attributes["session"] = data["session"]

        if "id" in data:
            self._attr_extra_state_attributes["device_id"] = data["id"]

        self.async_write_ha_state()


class TorqueAPIEndpointSensor(SensorEntity):
    """Sensor that displays the API endpoint URL for the Torque app."""

    _attr_should_poll = False
    _attr_icon = "mdi:api"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        vehicle_name: str,
    ) -> None:
        """Initialize the API endpoint sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._vehicle_name = vehicle_name

        self._attr_name = "API Endpoint"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_api_endpoint"

        _LOGGER.debug("Initialized API endpoint sensor for vehicle '%s'", vehicle_name)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Torque vehicle."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=self._vehicle_name,
            manufacturer="Torque",
            model="OBD-II",
        )

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        _LOGGER.info(
            "Added API endpoint sensor for vehicle '%s' to Home Assistant",
            self._vehicle_name,
        )

        if self._entry_id in self.hass.data.get(DOMAIN, {}):
            api_path = self.hass.data[DOMAIN][self._entry_id].get("api_path", "")
            if api_path:
                try:
                    base_url = network.get_url(self.hass)
                except network.NoURLAvailableError:
                    _LOGGER.warning(
                        "No Home Assistant URL is available for the API endpoint sensor. "
                        "API endpoint sensor will only show the path. "
                        "Configure a URL in Settings -> System -> Network."
                    )
                    self._attr_native_value = api_path
                else:
                    self._attr_native_value = f"{base_url.rstrip('/')}{api_path}"
                    _LOGGER.info(
                        "API endpoint URL for '%s': %s",
                        self._vehicle_name,
                        self._attr_native_value,
                    )

                self.async_write_ha_state()
            else:
                _LOGGER.error(
                    "API path not found in hass.data for entry_id %s",
                    self._entry_id,
                )
        else:
            _LOGGER.error(
                "Entry data not found for entry_id %s in hass.data[%s]",
                self._entry_id,
                DOMAIN,
            )


class TorqueLastUpdateSensor(RestoreEntity, SensorEntity):
    """Sensor that displays the last time Torque successfully pushed data."""

    _attr_should_poll = False
    _attr_icon = "mdi:clock-check-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        vehicle_name: str,
    ) -> None:
        """Initialize the last update sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._vehicle_name = vehicle_name

        self._attr_name = "Last Torque Update"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_last_torque_update"
        self._attr_native_value = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Torque vehicle."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=self._vehicle_name,
            manufacturer="Torque",
            model="OBD-II",
        )

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (
            None,
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
        ):
            try:
                self._attr_native_value = datetime.fromisoformat(last_state.state)
                self.async_write_ha_state()
            except (ValueError, TypeError):
                _LOGGER.error(
                    "Failed to restore the last update timestamp for vehicle '%s'",
                    self._vehicle_name,
                )

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_{self._entry_id}_update",
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self, data: dict[str, Any]) -> None:
        """Update the sensor with the current timestamp when a push occurs."""
        self._attr_native_value = dt_util.utcnow()
        self.async_write_ha_state()
