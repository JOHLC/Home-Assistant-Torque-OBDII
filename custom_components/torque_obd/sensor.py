"""Support for Torque OBD-II sensors."""
from __future__ import annotations

from datetime import datetime
import logging
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
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CONF_EMAIL, CONF_VEHICLE_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Torque sensors based on a config entry."""
    email = config_entry.data.get(CONF_EMAIL, "")
    vehicle_name = config_entry.data[CONF_VEHICLE_NAME]
    
    _LOGGER.info("Setting up Torque sensor platform for vehicle '%s'", vehicle_name)
    
    # Store the async_add_entities callback for dynamic sensor creation
    # Entry data should already exist from __init__.py, but check to be safe
    if config_entry.entry_id in hass.data.get(DOMAIN, {}):
        hass.data[DOMAIN][config_entry.entry_id]["async_add_entities"] = async_add_entities
        hass.data[DOMAIN][config_entry.entry_id]["added_sensors"] = set()
        hass.data[DOMAIN][config_entry.entry_id]["email"] = email
        hass.data[DOMAIN][config_entry.entry_id]["vehicle_name"] = vehicle_name
        _LOGGER.debug("Stored async_add_entities callback for entry %s", config_entry.entry_id)
    
    # Only add the API endpoint sensor upfront
    sensors = [
        TorqueAPIEndpointSensor(
            hass,
            config_entry.entry_id,
            vehicle_name,
        )
    ]
    
    async_add_entities(sensors, True)
    _LOGGER.debug("Added API endpoint sensor for vehicle '%s'", vehicle_name)


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
        
        _LOGGER.debug("Initialized sensor '%s' (PID: %s) for vehicle '%s'", 
                     self._attr_name, key, vehicle_name)

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
        
        _LOGGER.info("Added sensor '%s' (PID: %s) for vehicle '%s' to Home Assistant", self._attr_name, self._key, self._vehicle_name)
        
        # Restore previous state if available
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
            _LOGGER.info("Restoring previous state for sensor '%s': %s", self._attr_name, last_state.state)
            
            # Restore the native value
            try:
                self._attr_native_value = float(last_state.state)
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
                    _LOGGER.debug("Restored attributes for sensor '%s': %s", self._attr_name, self._attr_extra_state_attributes)
            
            # Write the restored state to Home Assistant
            self.async_write_ha_state()
            _LOGGER.debug("Wrote restored state to Home Assistant for sensor '%s'", self._attr_name)
        
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
                self._attr_native_value = float(value)
            except (ValueError, TypeError):
                self._attr_native_value = value
            
            # Log update only if value changed (to avoid spam)
            if old_value != self._attr_native_value:
                _LOGGER.debug("Sensor '%s' updated: %s -> %s", self._attr_name, old_value, self._attr_native_value)
            
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
        
        _LOGGER.info("Added API endpoint sensor for vehicle '%s' to Home Assistant", self._vehicle_name)
        
        # Get the API path from hass.data and set it as the sensor value
        if self._entry_id in self.hass.data.get(DOMAIN, {}):
            api_path = self.hass.data[DOMAIN][self._entry_id].get("api_path", "")
            if api_path:
                # Get the base URL from Home Assistant
                base_url = self.hass.config.external_url or self.hass.config.internal_url
                if base_url:
                    self._attr_native_value = f"{base_url}{api_path}"
                    _LOGGER.info("API endpoint URL for '%s': %s", self._vehicle_name, self._attr_native_value)
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
