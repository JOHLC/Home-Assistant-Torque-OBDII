"""Support for Torque OBD-II sensors."""

from __future__ import annotations

from datetime import datetime
import logging
import math
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.restore_state import RestoreEntity

from . import _normalize_pid
from .const import CONF_EMAIL, CONF_VEHICLE_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _create_default_sensor_definition(pid_key: str, entity_name: str | None = None) -> dict[str, Any]:
    """Create a default sensor definition for PIDs without predefined definitions.
    
    Args:
        pid_key: The PID key (e.g., "k05" or "kff1001")
        entity_name: Optional entity name from registry
        
    Returns:
        Dictionary with default sensor definition
    """
    return {
        "name": entity_name or f"PID {pid_key}",
        "unit": None,
        "icon": "mdi:car-info",
        "device_class": None,
        "state_class": None,
    }


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Torque sensors based on a config entry."""
    email = config_entry.data.get(CONF_EMAIL, "")
    vehicle_name = config_entry.data[CONF_VEHICLE_NAME]

    _LOGGER.info("Setting up Torque sensor platform for vehicle '%s'", vehicle_name)

    # Get sensor definitions for restoring sensors
    # Sensor definitions are loaded in __init__.py before platform setup
    sensor_definitions = hass.data.get(DOMAIN, {}).get("sensor_definitions", {})
    if not sensor_definitions:
        _LOGGER.warning(
            "Sensor definitions not found during sensor setup for %s. "
            "This is unexpected - definitions should be loaded in __init__.py",
            vehicle_name
        )

    # Ensure entry data exists (should already exist from __init__.py)
    # Create it if missing as a defensive measure
    hass.data.setdefault(DOMAIN, {}).setdefault(config_entry.entry_id, {})
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    
    # Initialize or update entry data with required fields
    entry_data.update({
        "async_add_entities": async_add_entities,
        "added_sensors": entry_data.get("added_sensors", set()),
        "email": email,
        "vehicle_name": vehicle_name,
    })

    # Always add the API endpoint sensor upfront
    sensors = [
        TorqueAPIEndpointSensor(
            hass,
            config_entry.entry_id,
            vehicle_name,
        )
    ]

    # Restore previously registered sensors from entity registry
    # This ensures sensors remain available after reboot until new data arrives
    entity_reg = er.async_get(hass)
    existing_entities = er.async_entries_for_config_entry(
        entity_reg, config_entry.entry_id
    )
    
    restored_count = 0
    for entity_entry in existing_entities:
        # Skip the API endpoint sensor (it's already added above)
        if entity_entry.unique_id.endswith("_api_endpoint"):
            continue
        
        # Extract the PID key from the unique_id
        # Format is: torque_obd_{entry_id}_{pid_key}
        # Use prefix matching for robust parsing regardless of entry_id format
        unique_id_prefix = f"{DOMAIN}_{config_entry.entry_id}_"
        if not entity_entry.unique_id.startswith(unique_id_prefix):
            _LOGGER.warning(
                "Unexpected unique_id format for entity %s: %s",
                entity_entry.entity_id,
                entity_entry.unique_id
            )
            continue
            
        pid_key = entity_entry.unique_id[len(unique_id_prefix):]
        
        # Normalize the PID for definition lookup
        normalized_pid = _normalize_pid(pid_key)
        
        # Get sensor definition if available (use normalized PID for lookup)
        definition = sensor_definitions.get(
            normalized_pid,
            _create_default_sensor_definition(pid_key, entity_entry.original_name)
        )
        
        # Override sensor name if entity has a custom name
        # We pass the custom name to TorqueSensor instead of copying the whole definition
        sensor_name = entity_entry.name if entity_entry.name else definition["name"]
        
        # Create the sensor to restore it (use original PID key)
        sensor = TorqueSensor(
            hass,
            config_entry.entry_id,
            email,
            vehicle_name,
            pid_key,  # Use original key as stored in unique_id
            {**definition, "name": sensor_name},  # Override name if custom
        )
        sensors.append(sensor)
        
        # Mark both original and normalized keys as added to prevent duplicates
        entry_data = hass.data[DOMAIN][config_entry.entry_id]
        entry_data["added_sensors"].add(pid_key)
        entry_data["added_sensors"].add(normalized_pid)
        
        restored_count += 1
        _LOGGER.debug(
            "Restoring sensor '%s' (PID: %s, normalized: %s) for vehicle '%s'",
            definition["name"],
            pid_key,
            normalized_pid,
            vehicle_name,
        )
    
    if restored_count > 0:
        _LOGGER.info(
            "Restored %d sensor(s) for vehicle '%s' from entity registry",
            restored_count,
            vehicle_name,
        )

    async_add_entities(sensors, True)
    _LOGGER.debug(
        "Added %d total sensor(s) for vehicle '%s' (including API endpoint)",
        len(sensors),
        vehicle_name,
    )


class TorqueSensor(RestoreEntity, SensorEntity):
    """Representation of a Torque OBD-II sensor."""

    _attr_should_poll = False

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
        self._definition = definition

        # Set sensor attributes
        # Prefix sensor name with vehicle name for proper entity ID generation
        self._attr_name = f"{vehicle_name} {definition['name']}"
        self._attr_native_unit_of_measurement = definition.get("unit")
        self._attr_icon = definition.get("icon")

        # Set device class if specified
        if definition.get("device_class"):
            self._attr_device_class = definition["device_class"]

        # Set state class if specified
        if definition.get("state_class"):
            self._attr_state_class = definition["state_class"]

        # Set default precision of 2 decimal places for numeric sensors
        # This can be overridden by users in the UI
        self._attr_suggested_display_precision = 2

        # Generate unique ID using entry_id for uniqueness
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{key}"

        # Set initial state
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

        _LOGGER.info(
            "Added sensor '%s' (PID: %s) for vehicle '%s' to Home Assistant",
            self._attr_name,
            self._key,
            self._vehicle_name,
        )

        # Restore previous state if available
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (
            None,
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
        ):
            _LOGGER.info(
                "Restoring previous state for sensor '%s': %s",
                self._attr_name,
                last_state.state,
            )

            # Restore the native value
            try:
                restored_value = float(last_state.state)
                # Check if the restored value is finite (not inf, -inf, or nan)
                if not math.isfinite(restored_value):
                    _LOGGER.debug(
                        "Sensor '%s' had non-finite restored state '%s', setting to None",
                        self._attr_name,
                        last_state.state
                    )
                    self._attr_native_value = None
                else:
                    self._attr_native_value = restored_value
            except (ValueError, TypeError):
                self._attr_native_value = last_state.state

            # Restore only custom extra state attributes (not HA internal attributes)
            if last_state.attributes:
                # Only restore our custom attributes that we set in _handle_update
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

            # Write the restored state to Home Assistant
            self.async_write_ha_state()
            _LOGGER.debug(
                "Wrote restored state to Home Assistant for sensor '%s'",
                self._attr_name,
            )

        # Register callback for data updates
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
        # Check if this sensor's key is in the data
        if self._key in data:
            value = data[self._key]
            old_value = self._attr_native_value

            # Try to convert to float
            try:
                converted_value = float(value)
                # Check if the value is finite (not inf, -inf, or nan)
                if not math.isfinite(converted_value):
                    _LOGGER.debug(
                        "Sensor '%s' received non-finite value '%s', setting to None",
                        self._attr_name,
                        value
                    )
                    self._attr_native_value = None
                else:
                    self._attr_native_value = converted_value
            except (ValueError, TypeError):
                # Keep non-numeric values as-is
                self._attr_native_value = value

            # Log update only if value changed (to avoid spam)
            if old_value != self._attr_native_value:
                _LOGGER.debug(
                    "Sensor '%s' updated: %s -> %s",
                    self._attr_name,
                    old_value,
                    self._attr_native_value,
                )

            # Update extra attributes
            self._attr_extra_state_attributes = {
                "last_update": datetime.now().isoformat(),
            }

            # Add session info if available
            if "session" in data:
                self._attr_extra_state_attributes["session"] = data["session"]

            # Add device ID if available
            if "id" in data:
                self._attr_extra_state_attributes["device_id"] = data["id"]

            # Schedule an update
            self.async_write_ha_state()


class TorqueAPIEndpointSensor(SensorEntity):
    """Sensor that displays the API endpoint URL for the Torque app."""

    _attr_should_poll = False
    _attr_icon = "mdi:api"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

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

        # Set sensor attributes
        # Prefix sensor name with vehicle name for proper entity ID generation
        self._attr_name = f"{vehicle_name} API Endpoint"
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

        # Get the API path from hass.data and set it as the sensor value
        if self._entry_id in self.hass.data.get(DOMAIN, {}):
            api_path = self.hass.data[DOMAIN][self._entry_id].get("api_path", "")
            if api_path:
                # Get the base URL from Home Assistant
                base_url = (
                    self.hass.config.external_url or self.hass.config.internal_url
                )
                if base_url:
                    self._attr_native_value = f"{base_url}{api_path}"
                    _LOGGER.info(
                        "API endpoint URL for '%s': %s",
                        self._vehicle_name,
                        self._attr_native_value,
                    )
                else:
                    # Fallback if no URL is configured
                    _LOGGER.warning(
                        "No external or internal URL configured for Home Assistant. "
                        "API endpoint sensor will only show the path. "
                        "Configure a URL in Settings -> System -> Network."
                    )
                    self._attr_native_value = api_path

                self.async_write_ha_state()
            else:
                _LOGGER.error(
                    "API path not found in hass.data for entry_id %s", self._entry_id
                )
        else:
            _LOGGER.error(
                "Entry data not found for entry_id %s in hass.data[%s]",
                self._entry_id,
                DOMAIN,
            )
