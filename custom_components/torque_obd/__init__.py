"""The Torque OBD-II integration."""
from __future__ import annotations

import logging
from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import CONF_EMAIL, CONF_VEHICLE_NAME, DOMAIN, ATTRIBUTE_FIELDS, METADATA_FIELD_PREFIXES, load_sensor_definitions

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def _extract_name_from_value(value: Any) -> str | None:
    """Extract name from value, handling arrays and strings.
    
    Args:
        value: The value which may be a string or array of strings
        
    Returns:
        The extracted name, or None if not available
    """
    if isinstance(value, list) and value:
        return value[0]
    elif isinstance(value, str):
        return value
    return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Torque OBD-II from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Load sensor definitions (defaults + custom overrides)
    # Load once and share across all entries
    if "sensor_definitions" not in hass.data[DOMAIN]:
        sensor_definitions = await hass.async_add_executor_job(
            load_sensor_definitions, hass
        )
        hass.data[DOMAIN]["sensor_definitions"] = sensor_definitions
        _LOGGER.debug("Loaded %d sensor definitions", len(sensor_definitions))
    
    # Get vehicle name and create URL-safe version
    vehicle_name = entry.data[CONF_VEHICLE_NAME]
    _LOGGER.info("Setting up Torque OBD-II for vehicle '%s' (entry_id: %s)", vehicle_name, entry.entry_id)
    # Normalize: lowercase, replace spaces with dashes, keep underscores and dashes
    # Remove any characters that aren't alphanumeric, dash, or underscore
    url_safe_name = vehicle_name.lower()
    url_safe_name = url_safe_name.replace(' ', '-')
    # Remove any remaining invalid characters
    url_safe_name = ''.join(c for c in url_safe_name if c.isalnum() or c in '-_')
    api_path = f"/api/torque-{url_safe_name}"
    
    # Store the config entry data
    hass.data[DOMAIN][entry.entry_id] = {
        "email": entry.data.get(CONF_EMAIL, ""),
        "vehicle_name": vehicle_name,
        "api_path": api_path,
        "data": {},
    }

    # Register a unique HTTP API view for this vehicle
    hass.http.register_view(TorqueView(hass, entry.entry_id, api_path))
    _LOGGER.info("Registered HTTP endpoint for '%s' at %s", vehicle_name, api_path)

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("Completed setup for Torque OBD-II entry '%s'", vehicle_name)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    vehicle_name = entry.data.get(CONF_VEHICLE_NAME, "Unknown")
    _LOGGER.info("Unloading Torque OBD-II for vehicle '%s' (entry_id: %s)", vehicle_name, entry.entry_id)
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug("Successfully unloaded Torque OBD-II entry '%s'", vehicle_name)
    else:
        _LOGGER.warning("Failed to unload platforms for Torque OBD-II entry '%s'", vehicle_name)

    return unload_ok


class TorqueView(HomeAssistantView):
    """Handle data from Torque requests."""

    requires_auth = False

    def __init__(self, hass: HomeAssistant, entry_id: str, api_path: str) -> None:
        """Initialize the Torque view."""
        self.hass = hass
        self.entry_id = entry_id
        self.url = api_path
        self.name = f"api:torque_{entry_id}"
        _LOGGER.debug("Initialized TorqueView for entry %s with path %s", entry_id, api_path)

    @callback
    async def get(self, request: web.Request) -> web.Response:
        """Handle Torque data via GET request."""
        return await self._handle_request(request)

    @callback
    async def post(self, request: web.Request) -> web.Response:
        """Handle Torque data via POST request."""
        return await self._handle_request(request)

    async def _create_sensors_for_new_data(self, data_dict: dict[str, Any]) -> None:
        """Create sensors dynamically for new data keys."""
        # Import here to avoid circular dependency between __init__ and sensor modules
        from .sensor import TorqueSensor
        
        # Check if entry still exists (may have been unloaded during request)
        if self.entry_id not in self.hass.data.get(DOMAIN, {}):
            _LOGGER.debug("Entry %s not found when creating sensors, integration may be unloading", self.entry_id)
            return
        
        entry_data = self.hass.data[DOMAIN][self.entry_id]
        added_sensors = entry_data.get("added_sensors", set())
        async_add_entities = entry_data.get("async_add_entities")
        
        if async_add_entities is None:
            _LOGGER.warning("async_add_entities not available for entry %s", self.entry_id)
            return
        
        # Get sensor definitions (loaded at setup time)
        sensor_definitions = self.hass.data[DOMAIN].get("sensor_definitions", {})
        
        # Initialize sensor names storage if not exists
        if "sensor_names" not in entry_data:
            entry_data["sensor_names"] = {}
        sensor_names = entry_data["sensor_names"]
        
        # First pass: Extract and store sensor names from payload
        # userFullName{PID} and userShortName{PID} come before k{PID} values
        for key, value in data_dict.items():
            if key.startswith("userFullName"):
                # Extract PID from userFullNameXXXX
                pid = key[12:]  # Remove "userFullName" prefix
                name_value = _extract_name_from_value(value)
                if pid and name_value:
                    if "k" + pid not in sensor_names:
                        sensor_names["k" + pid] = {
                            "full_name": name_value,
                            "short_name": None
                        }
                    else:
                        sensor_names["k" + pid]["full_name"] = name_value
                    _LOGGER.debug("Stored full name for PID k%s: %s", pid, name_value)
            elif key.startswith("userShortName"):
                # Extract PID from userShortNameXXXX
                pid = key[13:]  # Remove "userShortName" prefix
                name_value = _extract_name_from_value(value)
                if pid and name_value:
                    if "k" + pid not in sensor_names:
                        sensor_names["k" + pid] = {
                            "full_name": None,
                            "short_name": name_value
                        }
                    else:
                        sensor_names["k" + pid]["short_name"] = name_value
                    _LOGGER.debug("Stored short name for PID k%s: %s", pid, name_value)
        
        new_sensors = []
        
        # Second pass: Check each key in the incoming data for actual sensor values (k{PID})
        for key in data_dict.keys():
            # Skip if sensor already exists
            if key in added_sensors:
                continue
            
            # Skip metadata fields
            if key in ATTRIBUTE_FIELDS:
                continue
            
            # Skip fields that match metadata prefixes
            is_metadata = False
            for prefix in METADATA_FIELD_PREFIXES:
                if key.startswith(prefix):
                    is_metadata = True
                    break
            if is_metadata:
                continue
            
            # Only create sensors for data keys (k{PID})
            if not key.startswith("k"):
                continue
            
            # Determine sensor name from payload or definitions
            sensor_name = None
            if key in sensor_names:
                # Use full name if available, otherwise short name
                if sensor_names[key].get("full_name"):
                    sensor_name = sensor_names[key]["full_name"]
                elif sensor_names[key].get("short_name"):
                    sensor_name = sensor_names[key]["short_name"]
            
            # Check if we have a definition for this sensor
            if key in sensor_definitions:
                definition = sensor_definitions[key].copy()
                # Override name if we got one from payload
                if sensor_name:
                    definition["name"] = sensor_name
                    _LOGGER.debug("Using name from payload for PID '%s': %s", key, sensor_name)
            else:
                # Create a generic definition for undefined PIDs
                definition = {
                    "name": sensor_name if sensor_name else f"PID {key}",
                    "unit": None,
                    "icon": "mdi:car-info",
                    "device_class": None,
                    "state_class": None,
                }
                _LOGGER.info("Creating generic sensor for undefined PID: %s with name: %s", key, definition["name"])
            
            # Create the sensor
            sensor = TorqueSensor(
                self.hass,
                self.entry_id,
                entry_data.get("email", ""),
                entry_data.get("vehicle_name", "Unknown"),
                key,
                definition,
            )
            new_sensors.append(sensor)
            added_sensors.add(key)
            _LOGGER.debug("Creating new sensor '%s' for PID '%s'", definition["name"], key)
        
        # Add the new sensors if any
        if new_sensors:
            async_add_entities(new_sensors, True)
            vehicle_name = entry_data.get("vehicle_name", "Unknown")
            _LOGGER.info("Added %d new sensor(s) for vehicle '%s'", len(new_sensors), vehicle_name)

    async def _handle_request(self, request: web.Request) -> web.Response:
        """Process the Torque request."""
        try:
            # Get data from query parameters (GET) or form data (POST)
            if request.method == "POST":
                data = await request.post()
            else:
                data = request.query

            # Convert to regular dict for easier processing
            data_dict = dict(data)
            
            # Check if entry still exists in hass.data (it may have been unloaded)
            if self.entry_id not in self.hass.data.get(DOMAIN, {}):
                _LOGGER.warning(
                    "Received %s request on %s but entry_id %s not found. Integration may have been unloaded.",
                    request.method,
                    self.url,
                    self.entry_id,
                )
                return web.Response(text="OK!")
            
            entry_data = self.hass.data[DOMAIN][self.entry_id]
            vehicle_name = entry_data.get("vehicle_name", "Unknown")
            _LOGGER.debug("Received %s request for '%s' with %d parameters", request.method, vehicle_name, len(data_dict))

            # Store the latest data
            entry_data["data"] = data_dict
            _LOGGER.debug("Stored data for '%s': %d keys", vehicle_name, len(data_dict))

            # Check for new sensors and create them dynamically
            await self._create_sensors_for_new_data(data_dict)

            # Notify sensors about new data
            signal = f"{DOMAIN}_{self.entry_id}_update"
            async_dispatcher_send(
                self.hass,
                signal,
                data_dict,
            )
            _LOGGER.debug("Dispatched update signal '%s' for '%s'", signal, vehicle_name)

            return web.Response(text="OK!")

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Error processing Torque data on %s: %s", self.url, err, exc_info=True)
            # Return OK to Torque even on error to prevent retries and user-facing errors
            return web.Response(text="OK!")
