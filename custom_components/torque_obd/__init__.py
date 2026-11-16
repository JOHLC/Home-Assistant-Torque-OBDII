"""The Torque OBD-II integration."""
from __future__ import annotations

from hashlib import sha256
from hmac import compare_digest
from http import HTTPStatus
import logging
from typing import Any

from aiohttp import hdrs, web
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    ATTRIBUTE_FIELDS,
    CONF_EMAIL,
    CONF_UPLOAD_TOKEN_HASH,
    CONF_VEHICLE_NAME,
    DOMAIN,
    GPS_LATITUDE_PID,
    GPS_LONGITUDE_PID,
    METADATA_FIELD_PREFIXES,
    load_sensor_definitions,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.DEVICE_TRACKER]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

# Standard OBD-II PIDs (0x00-0xFF) use 2 hex digits
STANDARD_PID_HEX_LENGTH = 2


def _normalize_pid(pid: str) -> str:
    """Normalize PID format to ensure consistent format with leading zeros.
    
    Torque sends PIDs in different formats:
    - Short format: k5, kb, kc, kd, kf (without leading zeros)
    - Long format: k05, k0b, k0c, k0d, k0f (with leading zeros)
    - Extended format: k221e1c, k2203ca, etc. (longer than 2 hex digits)
    
    This function normalizes short PIDs to the long format used in const.py.
    Standard OBD-II PIDs (0x00-0xFF) should always be 2 hex digits.
    Extended PIDs with more than 2 hex digits remain unchanged.
    
    Args:
        pid: The PID string from Torque (e.g., "k5" or "k05")
        
    Returns:
        Normalized PID with leading zeros. Examples:
        - k5 -> k05 (short format normalized)
        - k0d -> k0d (long format unchanged)
        - k221e1c -> k221e1c (extended format unchanged)
    """
    if not pid.startswith("k"):
        return pid
    
    # Extract the hex part after 'k'
    hex_part = pid[1:]
    
    # Validate hex format for robustness - malformed PIDs are returned unchanged
    # This prevents crashes from invalid data while logging the issue
    try:
        int(hex_part, 16)  # Validate it's valid hexadecimal
    except ValueError:
        # If not valid hex, return as-is
        _LOGGER.debug("Invalid hex in PID '%s', returning as-is", pid)
        return pid
    
    # Only normalize if it's a short standard PID (1-2 hex digits)
    # Extended PIDs (kff*, k22*, etc.) are already in the correct format
    if len(hex_part) <= STANDARD_PID_HEX_LENGTH:
        # Pad with leading zero if needed for standard OBD-II PIDs
        hex_part = hex_part.zfill(STANDARD_PID_HEX_LENGTH)
    
    return f"k{hex_part}"


def _normalize_sensor_key(key: str) -> str:
    """Normalize a sensor PID while preserving its repeated-value index."""
    base_key, separator, value_index = key.rpartition("__")
    if not (separator and value_index.isdecimal() and base_key.startswith("k")):
        return _normalize_pid(key)

    return f"{_normalize_pid(base_key)}__{value_index}"


def _extract_name_from_value(value: Any, index: int = 0) -> str | None:
    """Extract indexed text from a string or array.
    
    Args:
        value: The value which may be a string or array of strings
        
    Returns:
        The extracted name, or None if not available
    """
    if isinstance(value, (list, tuple)) and len(value) > index:
        return value[index]
    elif isinstance(value, str):
        return value
    return None


def _request_data_to_dict(data: Any) -> dict[str, Any]:
    """Convert request data to a dict without dropping repeated fields."""
    getall = getattr(data, "getall", None)
    if getall is None:
        return dict(data)

    data_dict: dict[str, Any] = {}
    for key in data.keys():
        if key in data_dict:
            continue
        values = getall(key)
        data_dict[key] = values[0] if len(values) == 1 else values
    return data_dict


def _expand_duplicate_pid_values(data_dict: dict[str, Any]) -> dict[str, Any]:
    """Give repeated readings for a PID distinct internal keys."""
    expanded_data: dict[str, Any] = {}
    for key, value in data_dict.items():
        if (
            key.startswith("k")
            and isinstance(value, (list, tuple))
            and len(value) > 1
        ):
            expanded_data[key] = value[0]
            for index, reading in enumerate(value[1:], start=1):
                expanded_data[f"{key}__{index}"] = reading
        else:
            expanded_data[key] = value
    return expanded_data


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Torque OBD-II from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Load sensor definitions (defaults + custom overrides)
    if "sensor_definitions" not in hass.data[DOMAIN]:
        sensor_definitions = await hass.async_add_executor_job(
            load_sensor_definitions, hass
        )
        hass.data[DOMAIN]["sensor_definitions"] = sensor_definitions
        _LOGGER.debug("Loaded %d sensor definitions", len(sensor_definitions))
    
    vehicle_name = entry.data[CONF_VEHICLE_NAME]
    _LOGGER.info("Setting up Torque OBD-II for vehicle '%s' (entry_id: %s)", vehicle_name, entry.entry_id)
    
    url_safe_name = vehicle_name.lower().replace(' ', '-')
    url_safe_name = ''.join(c for c in url_safe_name if c.isalnum() or c in '-_')
    api_path = f"/api/torque-{url_safe_name}"
    
    # --- RECUPERO SENSORI ESISTENTI AL RIAVVIO (AGGIUNTO PER LA PR) ---
    from homeassistant.helpers import entity_registry as er
    entity_registry = er.async_get(hass)
    existing_pids = set()
    
    # Cerchiamo tutte le entità registrate che appartengono a questa ConfigEntry
    for entity_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
        # L'unique_id è registrato come: f"{DOMAIN}_{entry_id}_{key}"
        # Estraiamo la parte finale (la chiave PID come 'kd' o 'k0d')
        prefix = f"{DOMAIN}_{entry.entry_id}_"
        if entity_entry.unique_id.startswith(prefix):
            pid_key = entity_entry.unique_id[len(prefix):]
            if pid_key not in {"api_endpoint", "last_torque_update"}:
                existing_pids.add(_normalize_sensor_key(pid_key))
    
    _LOGGER.info("Found %d pre-existing PIDs in entity registry for %s", len(existing_pids), vehicle_name)
    # -----------------------------------------------------------------

    hass.data[DOMAIN][entry.entry_id] = {
        "email": entry.data.get(CONF_EMAIL, ""),
        "vehicle_name": vehicle_name,
        "api_path": api_path,
        "data": {},
        "added_sensors": existing_pids, # Passiamo subito i PID storici invece di un set() vuoto
    }

    hass.http.register_view(TorqueView(hass, entry.entry_id, api_path))
    _LOGGER.info("Registered HTTP endpoint for '%s' at %s", vehicle_name, api_path)

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
                # Normalize the PID format
                normalized_pid = _normalize_pid("k" + pid)
                if pid and value:
                    if normalized_pid not in sensor_names:
                        sensor_names[normalized_pid] = {
                            "full_name": value,
                            "short_name": None
                        }
                    else:
                        sensor_names[normalized_pid]["full_name"] = value
                    _LOGGER.debug("Stored full name for PID %s", normalized_pid)
            elif key.startswith("userShortName"):
                # Extract PID from userShortNameXXXX
                pid = key[13:]  # Remove "userShortName" prefix
                # Normalize the PID format
                normalized_pid = _normalize_pid("k" + pid)
                if pid and value:
                    if normalized_pid not in sensor_names:
                        sensor_names[normalized_pid] = {
                            "full_name": None,
                            "short_name": value
                        }
                    else:
                        sensor_names[normalized_pid]["short_name"] = value
                    _LOGGER.debug("Stored short name for PID %s", normalized_pid)
        
        new_sensors = []
        
        # Second pass: Check each key in the incoming data for actual sensor values (k{PID})
        for key in data_dict.keys():
            # Only process data keys (k{PID})
            if not key.startswith("k"):
                continue
            
            # Normalize the PID format for consistent lookups
            pid_key, separator, value_index = key.rpartition("__")
            if not (separator and value_index.isdecimal()):
                pid_key = key
                value_index = ""
            normalized_key = _normalize_pid(pid_key)
            normalized_sensor_key = _normalize_sensor_key(key)
            
            # Short and zero-padded PID aliases share one identity, while
            # repeated values remain distinct through their indexed suffix.
            if normalized_sensor_key in added_sensors:
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
            
            # Determine sensor name from payload or definitions
            sensor_name = None
            if normalized_key in sensor_names:
                name_index = int(value_index) if value_index else 0
                sensor_name = (
                    _extract_name_from_value(
                        sensor_names[normalized_key].get("full_name"), name_index
                    )
                    or _extract_name_from_value(
                        sensor_names[normalized_key].get("short_name"), name_index
                    )
                )
            
            # Check if we have a definition for this sensor (using normalized key)
            if normalized_key in sensor_definitions:
                definition = sensor_definitions[normalized_key].copy()
                # Override name if we got one from payload
                if sensor_name:
                    definition["name"] = sensor_name
                    _LOGGER.debug("Using name from payload for PID '%s' (original: '%s'): %s", normalized_key, key, sensor_name)
            else:
                # Create a generic definition for undefined PIDs
                definition = {
                    "name": sensor_name if sensor_name else f"PID {pid_key}",
                    "unit": None,
                    "icon": "mdi:car-info",
                    "device_class": None,
                    "state_class": None,
                }
                _LOGGER.debug("Creating generic sensor for undefined PID '%s' (original: '%s') with name: %s", normalized_key, key, definition["name"])

            # Use original key for data lookup - data_dict contains non-normalized PIDs from Torque
            sensor = TorqueSensor(
                self.hass,
                self.entry_id,
                entry_data.get("email", ""),
                entry_data.get("vehicle_name", "Unknown"),
                key,  # Original key (e.g., "kd") matches data_dict keys from Torque
                definition,
            )
            new_sensors.append(sensor)
            # Keep the first repeated value under its original PID identity for
            # compatibility; later values use indexed identities.
            added_sensors.add(normalized_sensor_key)
            _LOGGER.debug("Creating new sensor '%s' for PID '%s' (normalized: '%s')", definition["name"], key, normalized_key)
        
        # Add the new sensors if any
        if new_sensors:
            async_add_entities(new_sensors, True)
            vehicle_name = entry_data.get("vehicle_name", "Unknown")
            _LOGGER.info("Added %d new sensor(s) for vehicle '%s'", len(new_sensors), vehicle_name)

        # Create the GPS device tracker the first time both latitude and longitude
        # PIDs are present in the payload (create-on-demand so it never shows as
        # unavailable for vehicles without GPS enabled).
        if (
            GPS_LATITUDE_PID in data_dict
            and GPS_LONGITUDE_PID in data_dict
            and not entry_data.get("tracker_added", False)
            and entry_data.get("async_add_tracker") is not None
        ):
            from .device_tracker import TorqueDeviceTracker

            tracker = TorqueDeviceTracker(
                self.hass,
                self.entry_id,
                entry_data.get("vehicle_name", "Unknown"),
            )
            entry_data["tracker_added"] = True
            entry_data["async_add_tracker"]([tracker], True)
            _LOGGER.info(
                "Created GPS device tracker for vehicle '%s'",
                entry_data.get("vehicle_name", "Unknown"),
            )

    @staticmethod
    def _unauthorized_response() -> web.Response:
        """Reject an upload without counting it as a Home Assistant login failure."""
        return web.Response(
            status=HTTPStatus.UNAUTHORIZED,
            headers={hdrs.WWW_AUTHENTICATE: "Bearer"},
        )

    async def _handle_request(self, request: web.Request) -> web.Response:
        """Process an upload for the vehicle assigned to this URL."""
        entry = self.hass.config_entries.async_get_entry(self.entry_id)
        if entry is None:
            return web.Response(text="OK!")

        token_hash = entry.options.get(CONF_UPLOAD_TOKEN_HASH)
        if token_hash is not None:
            authorization = request.headers.getall(hdrs.AUTHORIZATION, [])
            header = authorization[0] if len(authorization) == 1 else ""
            scheme, _, token = header.partition(" ")
            token = token.lstrip(" ")
            if (
                scheme.lower() != "bearer"
                or not token
                or not token.isascii()
                or not compare_digest(
                    sha256(token.encode("ascii")).hexdigest(), token_hash
                )
            ):
                return self._unauthorized_response()

        try:
            # Get data from query parameters (GET) or form data (POST)
            if request.method == "POST":
                data = await request.post()
            else:
                data = request.query

            # Convert to regular dict for easier processing
            data_dict = _expand_duplicate_pid_values(_request_data_to_dict(data))
            
            # Check if entry still exists in hass.data (it may have been unloaded)
            if self.entry_id not in self.hass.data.get(DOMAIN, {}):
                _LOGGER.warning(
                    "Received %s request on %s but entry_id %s not found. Integration may have been unloaded.",
                    request.method,
                    self.url,
                    self.entry_id,
                )
                return web.Response(text="OK!")
            
            # POST body parsing can yield while the configured token changes.
            if entry.options.get(CONF_UPLOAD_TOKEN_HASH) != token_hash:
                return self._unauthorized_response()

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
