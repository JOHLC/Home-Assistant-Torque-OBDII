"""Support for Torque OBD-II GPS device tracker."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_GPS_ACCURACY, ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_VEHICLE_NAME,
    DOMAIN,
    GPS_ACCURACY_PID,
    GPS_ALTITUDE_PID,
    GPS_BEARING_PID,
    GPS_LATITUDE_PID,
    GPS_LONGITUDE_PID,
    GPS_SPEED_PID,
)

_LOGGER = logging.getLogger(__name__)

# Unique ID suffix for the device tracker entity within a config entry
TRACKER_UNIQUE_ID_SUFFIX = "device_tracker"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Torque GPS device tracker from a config entry.

    The tracker entity is created on-demand the first time GPS coordinates are
    received from the Torque app (see TorqueView._create_entities_for_new_data in
    __init__.py).  If the entity was already registered in a previous run it is
    restored immediately from the entity registry so Home Assistant can show the
    last known position right away.
    """
    vehicle_name = config_entry.data[CONF_VEHICLE_NAME]

    _LOGGER.debug(
        "Setting up Torque device tracker platform for vehicle '%s'", vehicle_name
    )

    hass.data.setdefault(DOMAIN, {}).setdefault(config_entry.entry_id, {})
    entry_data = hass.data[DOMAIN][config_entry.entry_id]

    # Store the callback so TorqueView can add the entity when GPS data first arrives
    entry_data["async_add_tracker"] = async_add_entities
    entry_data["tracker_added"] = False

    # Restore the tracker if it was previously registered in the entity registry
    unique_id = f"{DOMAIN}_{config_entry.entry_id}_{TRACKER_UNIQUE_ID_SUFFIX}"
    entity_registry = er.async_get(hass)
    existing_entity_id = entity_registry.async_get_entity_id(
        "device_tracker", DOMAIN, unique_id
    )
    if existing_entity_id is not None:
        _LOGGER.debug(
            "Restoring device tracker for vehicle '%s' (entity_id: %s)",
            vehicle_name,
            existing_entity_id,
        )
        tracker = TorqueDeviceTracker(
            hass,
            config_entry.entry_id,
            vehicle_name,
        )
        entry_data["tracker_added"] = True
        async_add_entities([tracker], True)
        _LOGGER.info("Restored device tracker for vehicle '%s'", vehicle_name)


class TorqueDeviceTracker(RestoreEntity, TrackerEntity):
    """GPS device tracker entity for a Torque OBD-II vehicle.

    The entity is only created once the Torque app sends GPS latitude and
    longitude values, so it will never appear as unavailable in the UI for
    vehicles that do not have GPS enabled.  Once created it persists across
    Home Assistant restarts and restores the last known coordinates from the
    state store.
    """

    _attr_should_poll = False
    _attr_source_type = SourceType.GPS
    # Override the DIAGNOSTIC category set by BaseTrackerEntity so the tracker
    # appears as a primary entity (useful for zone/presence automations).
    _attr_entity_category = None
    _attr_icon = "mdi:car-connected"

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        vehicle_name: str,
    ) -> None:
        """Initialize the GPS device tracker."""
        self.hass = hass
        self._entry_id = entry_id
        self._vehicle_name = vehicle_name

        # Entity name equals the vehicle name; no device linkage (device_info
        # is intentionally None for all TrackerEntity subclasses in HA).
        self._attr_name = vehicle_name
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{TRACKER_UNIQUE_ID_SUFFIX}"
        self._attr_latitude = None
        self._attr_longitude = None
        self._attr_location_accuracy = 0
        self._attr_extra_state_attributes: dict[str, Any] = {}

        _LOGGER.debug(
            "Initialized GPS device tracker for vehicle '%s'", vehicle_name
        )

    async def async_added_to_hass(self) -> None:
        """Restore the last known GPS location and subscribe to Torque updates."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            attrs = last_state.attributes
            try:
                lat = attrs.get(ATTR_LATITUDE)
                lon = attrs.get(ATTR_LONGITUDE)
                if lat is not None and lon is not None:
                    self._attr_latitude = float(lat)
                    self._attr_longitude = float(lon)

                    accuracy = attrs.get(ATTR_GPS_ACCURACY)
                    if accuracy is not None:
                        self._attr_location_accuracy = float(accuracy)

                    # Restore optional attributes (bearing, altitude, speed)
                    extra: dict[str, Any] = {}
                    for key in ("bearing", "altitude", "speed"):
                        if key in attrs:
                            extra[key] = attrs[key]
                    self._attr_extra_state_attributes = extra

                    _LOGGER.debug(
                        "Restored GPS location for vehicle '%s'",
                        self._vehicle_name,
                    )
                    self.async_write_ha_state()
            except (ValueError, TypeError):
                _LOGGER.debug(
                    "Could not restore GPS location for vehicle '%s'",
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
        """Handle new GPS data dispatched by TorqueView."""
        lat_raw = data.get(GPS_LATITUDE_PID)
        lon_raw = data.get(GPS_LONGITUDE_PID)

        if lat_raw is None or lon_raw is None:
            # GPS values not in this payload – keep previous location
            return

        try:
            lat = float(lat_raw)
            lon = float(lon_raw)
        except (ValueError, TypeError):
            _LOGGER.debug(
                "Invalid GPS coordinates for vehicle '%s': lat=%s, lon=%s",
                self._vehicle_name,
                lat_raw,
                lon_raw,
            )
            return

        self._attr_latitude = lat
        self._attr_longitude = lon

        # Update accuracy when available
        accuracy_raw = data.get(GPS_ACCURACY_PID)
        if accuracy_raw is not None:
            try:
                self._attr_location_accuracy = float(accuracy_raw)
            except (ValueError, TypeError):
                pass

        # Update optional extra attributes
        extra: dict[str, Any] = {}

        bearing_raw = data.get(GPS_BEARING_PID)
        if bearing_raw is not None:
            try:
                extra["bearing"] = float(bearing_raw)
            except (ValueError, TypeError):
                pass

        altitude_raw = data.get(GPS_ALTITUDE_PID)
        if altitude_raw is not None:
            try:
                extra["altitude"] = float(altitude_raw)
            except (ValueError, TypeError):
                pass

        speed_raw = data.get(GPS_SPEED_PID)
        if speed_raw is not None:
            try:
                extra["speed"] = float(speed_raw)
            except (ValueError, TypeError):
                pass

        self._attr_extra_state_attributes = extra
        self.async_write_ha_state()
