"""Constants for the Torque OBD-II integration."""
from __future__ import annotations

import logging
import os
from typing import Any, Final

import yaml

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolume,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN: Final = "torque_obd"

# Custom sensor definitions file
SENSOR_DEFINITIONS_FILE: Final = "torque_sensor_definitions.yaml"

# Configuration
CONF_EMAIL: Final = "email"
CONF_VEHICLE_NAME: Final = "vehicle_name"

# Sensor definitions
# Maps Torque parameter names to Home Assistant sensor attributes
# NOTE: These are FALLBACK definitions. Sensor names should preferably come from
# Torque payload (userFullName{PID} or userShortName{PID}) when available.
# Units are in METRIC format as Torque always sends metric values regardless of app settings:
# - Temperature: Celsius (°C)
# - Speed: Kilometers per hour (km/h)
# - Distance: Kilometers (km)
# - Volume: Liters (L)
# - Pressure: Kilopascals (kPa)
SENSOR_DEFINITIONS: Final = {
    # Speed sensors
    "kd": {
        "name": "Vehicle Speed",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:speedometer",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1006": {
        "name": "GPS Speed",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:map-marker-distance",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Engine sensors
    "kc": {
        "name": "Engine RPM",
        "unit": "RPM",
        "icon": "mdi:engine",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k5": {
        "name": "Engine Coolant Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:coolant-temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k46": {
        "name": "Ambient Air Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k5902": {
        "name": "Engine Oil Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:oil-temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kf": {
        "name": "Intake Air Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:air-filter",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k10": {
        "name": "MAF Air Flow Rate",
        "unit": "g/s",
        "icon": "mdi:air-filter",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Fuel sensors
    "k2f": {
        "name": "Fuel Level",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1271": {
        "name": "Fuel Remaining",
        "unit": UnitOfVolume.LITERS,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1270": {
        "name": "Fuel Used (Trip)",
        "unit": UnitOfVolume.LITERS,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kff1205": {
        "name": "Average Fuel Economy",
        "unit": "L/100km",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff5202": {
        "name": "Instant Fuel Economy",
        "unit": "L/100km",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Throttle and load
    "k11": {
        "name": "Throttle Position",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k4": {
        "name": "Engine Load",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Battery
    "kff1238": {
        "name": "Battery Voltage",
        "unit": "V",
        "icon": "mdi:car-battery",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # GPS sensors
    "kff1001": {
        "name": "GPS Latitude",
        "unit": "°",
        "icon": "mdi:crosshairs-gps",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1002": {
        "name": "GPS Longitude",
        "unit": "°",
        "icon": "mdi:crosshairs-gps",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1005": {
        "name": "GPS Altitude",
        "unit": "m",
        "icon": "mdi:elevation-rise",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1010": {
        "name": "GPS Bearing",
        "unit": "°",
        "icon": "mdi:compass",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Distance and time
    "kff1266": {
        "name": "Trip Distance",
        "unit": "km",
        "icon": "mdi:map-marker-distance",
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kff1204": {
        "name": "Trip Time (Since Journey Start)",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    # Timing
    "ke": {
        "name": "Timing Advance",
        "unit": "°",
        "icon": "mdi:clock-fast",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Pressure
    "k33": {
        "name": "Barometric Pressure",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "ka": {
        "name": "Fuel Pressure",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kb": {
        "name": "Intake Manifold Pressure",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
}

# Additional attributes to store but not create sensors for
ATTRIBUTE_FIELDS: Final = [
    "eml",  # Email address (vehicle identifier)
    "time",  # Timestamp
    "session",  # Session ID
    "id",  # Device ID
    "v",  # App version
]

# Patterns for fields that should not create sensors
# These are metadata fields from Torque
METADATA_FIELD_PREFIXES: Final = [
    "profile",  # Vehicle profile data (profileName, profileFuelType, etc.)
    "userUnit",  # User-configured units (DO NOT USE - frequently wrong)
    "defaultUnit",  # Default units (DO NOT USE - frequently wrong)
    "userShortName",  # Short names for PIDs (used for sensor naming)
    "userFullName",  # Full names for PIDs (used for sensor naming)
]


def load_sensor_definitions(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    """Load sensor definitions from YAML file if it exists, merge with defaults.
    
    Args:
        hass: Home Assistant instance
        
    Returns:
        Dictionary of sensor definitions (defaults merged with user customizations)
    """
    # Start with default definitions
    definitions = SENSOR_DEFINITIONS.copy()
    
    # Path to the custom sensor definitions file in the config directory
    config_path = hass.config.path(SENSOR_DEFINITIONS_FILE)
    
    if not os.path.isfile(config_path):
        _LOGGER.debug(
            "No custom sensor definitions file found at %s. Using defaults only.",
            config_path
        )
        return definitions
    
    try:
        _LOGGER.info("Loading custom sensor definitions from %s", config_path)
        with open(config_path, "r", encoding="utf-8") as file:
            custom_definitions = yaml.safe_load(file)
        
        if not custom_definitions:
            _LOGGER.warning(
                "Custom sensor definitions file at %s is empty or invalid. Using defaults only.",
                config_path
            )
            return definitions
        
        if not isinstance(custom_definitions, dict):
            _LOGGER.error(
                "Custom sensor definitions file at %s must contain a dictionary. Using defaults only.",
                config_path
            )
            return definitions
        
        # Merge custom definitions with defaults
        # Custom definitions override defaults
        merged_count = 0
        new_count = 0
        
        for pid, definition in custom_definitions.items():
            if not isinstance(definition, dict):
                _LOGGER.warning(
                    "Invalid definition for PID '%s' in custom sensor definitions. Skipping.",
                    pid
                )
                continue
            
            # Validate required fields
            if "name" not in definition:
                _LOGGER.warning(
                    "PID '%s' in custom sensor definitions missing required 'name' field. Skipping.",
                    pid
                )
                continue
            
            # Convert string class names to actual classes if needed
            definition_copy = definition.copy()
            
            # Handle device_class
            if "device_class" in definition_copy:
                device_class = definition_copy["device_class"]
                if isinstance(device_class, str) and device_class:
                    # Try to convert string to SensorDeviceClass
                    # Use getattr with None default to safely check for attribute
                    class_attr = getattr(SensorDeviceClass, device_class.upper(), None)
                    if class_attr is not None:
                        definition_copy["device_class"] = class_attr
                    else:
                        _LOGGER.warning(
                            "Unknown device_class '%s' for PID '%s'. Setting to None.",
                            device_class,
                            pid
                        )
                        definition_copy["device_class"] = None
            
            # Handle state_class
            if "state_class" in definition_copy:
                state_class = definition_copy["state_class"]
                if isinstance(state_class, str) and state_class:
                    # Try to convert string to SensorStateClass
                    # Use getattr with None default to safely check for attribute
                    class_attr = getattr(SensorStateClass, state_class.upper(), None)
                    if class_attr is not None:
                        definition_copy["state_class"] = class_attr
                    else:
                        _LOGGER.warning(
                            "Unknown state_class '%s' for PID '%s'. Setting to None.",
                            state_class,
                            pid
                        )
                        definition_copy["state_class"] = None
            
            # Add defaults for optional fields if not present
            definition_copy.setdefault("unit", None)
            definition_copy.setdefault("icon", "mdi:car-info")
            definition_copy.setdefault("device_class", None)
            definition_copy.setdefault("state_class", None)
            
            # Track if this is new or override
            if pid in definitions:
                merged_count += 1
                _LOGGER.debug("Overriding default definition for PID '%s'", pid)
            else:
                new_count += 1
                _LOGGER.debug("Adding new custom definition for PID '%s'", pid)
            
            definitions[pid] = definition_copy
        
        _LOGGER.info(
            "Loaded custom sensor definitions: %d overrides, %d new PIDs",
            merged_count,
            new_count
        )
        
    except yaml.YAMLError as err:
        _LOGGER.error(
            "Error parsing custom sensor definitions file at %s: %s. Using defaults only.",
            config_path,
            err,
            exc_info=True
        )
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.error(
            "Unexpected error loading custom sensor definitions from %s: %s. Using defaults only.",
            config_path,
            err,
            exc_info=True
        )
    
    return definitions
