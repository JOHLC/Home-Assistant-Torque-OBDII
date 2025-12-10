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
# Units are in METRIC format as Torque typically sends metric values regardless of app settings:
# - Temperature: Celsius (°C)
# - Speed: Kilometers per hour (km/h)
# - Distance: Kilometers (km)
# - Volume: Liters (L)
# - Pressure: Kilopascals (kPa)
# Note: While Torque usually sends metric values, this may vary by version or configuration.
SENSOR_DEFINITIONS: Final = {
    # Basic OBD-II sensors (0x00-0x1F)
    "k03": {
        "name": "Fuel Status",
        "unit": None,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": None,
    },
    "k04": {
        "name": "Engine Load",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k05": {
        "name": "Engine Coolant Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:coolant-temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k06": {
        "name": "Fuel Trim Bank 1 Short Term",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k07": {
        "name": "Fuel Trim Bank 1 Long Term",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k08": {
        "name": "Fuel Trim Bank 2 Short Term",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k09": {
        "name": "Fuel Trim Bank 2 Long Term",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k0a": {
        "name": "Fuel Pressure",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k0b": {
        "name": "Intake Manifold Pressure",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k0c": {
        "name": "Engine RPM",
        "unit": "RPM",
        "icon": "mdi:engine",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k0d": {
        "name": "Vehicle Speed",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:speedometer",
        "device_class": SensorDeviceClass.SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k0e": {
        "name": "Timing Advance",
        "unit": "°",
        "icon": "mdi:clock-fast",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k0f": {
        "name": "Intake Air Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:air-filter",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k10": {
        "name": "Mass Air Flow Rate",
        "unit": "g/s",
        "icon": "mdi:air-filter",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k11": {
        "name": "Throttle Position",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k12": {
        "name": "Air Status",
        "unit": None,
        "icon": "mdi:air-filter",
        "device_class": None,
        "state_class": None,
    },
    "k14": {
        "name": "Fuel Trim Bank 1 Sensor 1",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k15": {
        "name": "Fuel Trim Bank 1 Sensor 2",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k16": {
        "name": "Fuel Trim Bank 1 Sensor 3",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k17": {
        "name": "Fuel Trim Bank 1 Sensor 4",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k18": {
        "name": "Fuel Trim Bank 2 Sensor 1",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k19": {
        "name": "Fuel Trim Bank 2 Sensor 2",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k1a": {
        "name": "Fuel Trim Bank 2 Sensor 3",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k1b": {
        "name": "Fuel Trim Bank 2 Sensor 4",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k1f": {
        "name": "Run time since engine start",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    # OBD-II sensors (0x20-0x3F)
    "k21": {
        "name": "Distance travelled with MIL/CEL lit",
        "unit": "km",
        "icon": "mdi:map-marker-distance",
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "k22": {
        "name": "Fuel Rail Pressure (relative to manifold vacuum)",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k23": {
        "name": "Fuel Rail Pressure",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k24": {
        "name": "O2 Sensor1 Equivalence Ratio",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k25": {
        "name": "O2 Sensor2 Equivalence Ratio",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k26": {
        "name": "O2 Sensor3 Equivalence Ratio",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k27": {
        "name": "O2 Sensor4 Equivalence Ratio",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k28": {
        "name": "O2 Sensor5 Equivalence Ratio",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k29": {
        "name": "O2 Sensor6 Equivalence Ratio",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k2a": {
        "name": "O2 Sensor7 Equivalence Ratio",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k2b": {
        "name": "O2 Sensor8 Equivalence Ratio",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k2c": {
        "name": "EGR Commanded",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k2d": {
        "name": "EGR Error",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k2f": {
        "name": "Fuel Level",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k31": {
        "name": "Distance travelled since codes cleared",
        "unit": "km",
        "icon": "mdi:map-marker-distance",
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "k32": {
        "name": "Evap System Vapour Pressure",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k33": {
        "name": "Barometric Pressure",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k34": {
        "name": "O2 Sensor1 Equivalence Ratio (alternate)",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k3c": {
        "name": "Catalyst Temperature (Bank 1 Sensor 1)",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:coolant-temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k3d": {
        "name": "Catalyst Temperature (Bank 2 Sensor 1)",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:coolant-temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k3e": {
        "name": "Catalyst Temperature (Bank 1 Sensor 2)",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:coolant-temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k3f": {
        "name": "Catalyst Temperature (Bank 2 Sensor 2)",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:coolant-temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # OBD-II sensors (0x40-0x5F)
    "k42": {
        "name": "Voltage (Control Module)",
        "unit": "V",
        "icon": "mdi:car-battery",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k43": {
        "name": "Engine Load (Absolute)",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k44": {
        "name": "Commanded Equivalence Ratio (lambda)",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k45": {
        "name": "Relative Throttle Position",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k46": {
        "name": "Ambient Air Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k47": {
        "name": "Absolute Throttle Position B",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k49": {
        "name": "Accelerator Pedal Position D",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k4a": {
        "name": "Accelerator Pedal Position E",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k4b": {
        "name": "Accelerator Pedal Position F",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k52": {
        "name": "Ethanol Fuel %",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k5a": {
        "name": "Relative Accelerator Pedal Position",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k5c": {
        "name": "Engine Oil Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:oil-temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # OBD-II sensors (0x60+)
    "k78": {
        "name": "Exhaust Gas Temperature 1",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k79": {
        "name": "Exhaust Gas Temperature 2",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "ka6": {
        "name": "Odometer",
        "unit": "km",
        "icon": "mdi:counter",
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kb4": {
        "name": "Transmission Temperature (Method 2)",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Torque custom PIDs (kff*)
    "kff1001": {
        "name": "GPS Speed",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:map-marker-distance",
        "device_class": SensorDeviceClass.SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1005": {
        "name": "GPS Longitude",
        "unit": "°",
        "icon": "mdi:crosshairs-gps",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1006": {
        "name": "GPS Latitude",
        "unit": "°",
        "icon": "mdi:crosshairs-gps",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1010": {
        "name": "GPS Altitude",
        "unit": "m",
        "icon": "mdi:elevation-rise",
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1201": {
        "name": "Miles Per Gallon (Instant)",
        "unit": "mpg",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1202": {
        "name": "Turbo Boost & Vacuum Gauge",
        "unit": "psi",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1203": {
        "name": "Kilometers Per Litre (Instant)",
        "unit": "km/L",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1204": {
        "name": "Trip Distance",
        "unit": "km",
        "icon": "mdi:map-marker-distance",
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kff1205": {
        "name": "Trip average MPG",
        "unit": "mpg",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1206": {
        "name": "Trip average KPL",
        "unit": "km/L",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1207": {
        "name": "Litres Per 100 Kilometer (Instant)",
        "unit": "L/100km",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1208": {
        "name": "Trip average Litres/100 KM",
        "unit": "L/100km",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff120c": {
        "name": "Trip distance (stored in vehicle profile)",
        "unit": "km",
        "icon": "mdi:map-marker-distance",
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kff1214": {
        "name": "O2 Volts Bank 1 Sensor 1",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1215": {
        "name": "O2 Volts Bank 1 Sensor 2",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1216": {
        "name": "O2 Volts Bank 1 Sensor 3",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1217": {
        "name": "O2 Volts Bank 1 Sensor 4",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1218": {
        "name": "O2 Volts Bank 2 Sensor 1",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1219": {
        "name": "O2 Volts Bank 2 Sensor 2",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff121a": {
        "name": "O2 Volts Bank 2 Sensor 3",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff121b": {
        "name": "O2 Volts Bank 2 Sensor 4",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1220": {
        "name": "Acceleration Sensor (X axis)",
        "unit": "g",
        "icon": "mdi:car-speed-limiter",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1221": {
        "name": "Acceleration Sensor (Y axis)",
        "unit": "g",
        "icon": "mdi:car-speed-limiter",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1222": {
        "name": "Acceleration Sensor (Z axis)",
        "unit": "g",
        "icon": "mdi:car-speed-limiter",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1223": {
        "name": "Acceleration Sensor (Total)",
        "unit": "g",
        "icon": "mdi:car-speed-limiter",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1225": {
        "name": "Torque",
        "unit": "Nm",
        "icon": "mdi:engine",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1226": {
        "name": "Horsepower (At the wheels)",
        "unit": "hp",
        "icon": "mdi:engine",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff122d": {
        "name": "0-60mph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff122e": {
        "name": "0-100kph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff122f": {
        "name": "1/4 mile time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1230": {
        "name": "1/8 mile time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1237": {
        "name": "GPS vs OBD Speed difference",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:speedometer",
        "device_class": SensorDeviceClass.SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1238": {
        "name": "Voltage (OBD Adapter)",
        "unit": "V",
        "icon": "mdi:car-battery",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1239": {
        "name": "GPS Accuracy",
        "unit": "m",
        "icon": "mdi:crosshairs-gps",
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff123a": {
        "name": "GPS Satellites",
        "unit": None,
        "icon": "mdi:satellite-variant",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff123b": {
        "name": "GPS Bearing",
        "unit": "°",
        "icon": "mdi:compass",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1240": {
        "name": "O2 Sensor1 wide-range Voltage",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1241": {
        "name": "O2 Sensor2 wide-range Voltage",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1242": {
        "name": "O2 Sensor3 wide-range Voltage",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1243": {
        "name": "O2 Sensor4 wide-range Voltage",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1244": {
        "name": "O2 Sensor5 wide-range Voltage",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1245": {
        "name": "O2 Sensor6 wide-range Voltage",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1246": {
        "name": "O2 Sensor7 wide-range Voltage",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1247": {
        "name": "O2 Sensor8 wide-range Voltage",
        "unit": "V",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1249": {
        "name": "Air Fuel Ratio (Measured)",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff124a": {
        "name": "Tilt (x)",
        "unit": "°",
        "icon": "mdi:axis-arrow",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff124b": {
        "name": "Tilt (y)",
        "unit": "°",
        "icon": "mdi:axis-arrow",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff124c": {
        "name": "Tilt (z)",
        "unit": "°",
        "icon": "mdi:axis-arrow",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff124d": {
        "name": "Air Fuel Ratio (Commanded)",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff124f": {
        "name": "0-200kph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1257": {
        "name": "CO₂ in g/km (Instantaneous)",
        "unit": "g/km",
        "icon": "mdi:molecule-co2",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1258": {
        "name": "CO₂ in g/km (Average)",
        "unit": "g/km",
        "icon": "mdi:molecule-co2",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff125a": {
        "name": "Fuel flow rate/minute",
        "unit": "L/min",
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff125c": {
        "name": "Fuel cost (trip)",
        "unit": None,
        "icon": "mdi:currency-usd",
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kff125d": {
        "name": "Fuel flow rate/hour",
        "unit": "L/h",
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff125e": {
        "name": "60-120mph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff125f": {
        "name": "60-80mph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1260": {
        "name": "40-60mph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1261": {
        "name": "80-100mph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1263": {
        "name": "Average trip speed (whilst moving only)",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:speedometer",
        "device_class": SensorDeviceClass.SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1264": {
        "name": "100-0kph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1265": {
        "name": "60-0mph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1266": {
        "name": "Trip Time (Since journey start)",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kff1267": {
        "name": "Trip time (whilst stationary)",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kff1268": {
        "name": "Trip Time (whilst moving)",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kff1269": {
        "name": "Volumetric Efficiency (Calculated)",
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff126a": {
        "name": "Distance to empty (Estimated)",
        "unit": "km",
        "icon": "mdi:map-marker-distance",
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff126b": {
        "name": "Fuel Remaining (Calculated from vehicle profile)",
        "unit": PERCENTAGE,
        "icon": "mdi:fuel",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff126d": {
        "name": "Cost per mile/km (Instant)",
        "unit": None,
        "icon": "mdi:currency-usd",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff126e": {
        "name": "Cost per mile/km (Trip)",
        "unit": None,
        "icon": "mdi:currency-usd",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1270": {
        "name": "Barometer (on Android device)",
        "unit": "kPa",
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1271": {
        "name": "Fuel used (trip)",
        "unit": UnitOfVolume.LITERS,
        "icon": "mdi:fuel",
        "device_class": SensorDeviceClass.VOLUME,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "kff1272": {
        "name": "Average trip speed (whilst stopped or moving)",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:speedometer",
        "device_class": SensorDeviceClass.SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1273": {
        "name": "Engine kW (At the wheels)",
        "unit": "kW",
        "icon": "mdi:engine",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff1275": {
        "name": "80-120kph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1276": {
        "name": "60-130mph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff1277": {
        "name": "0-30mph Time",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
    },
    "kff5201": {
        "name": "Miles Per Gallon (Long Term Average)",
        "unit": "mpg",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff5202": {
        "name": "Kilometers Per Litre (Long Term Average)",
        "unit": "km/L",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kff5203": {
        "name": "Litres Per 100 Kilometer (Long Term Average)",
        "unit": "L/100km",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kfe1805": {
        "name": "Transmission Temperature (Method 1)",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Ford-specific extended PIDs
    "k221e1c": {
        "name": "Ford Transmission Temperature",
        "unit": UnitOfTemperature.FAHRENHEIT,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k2203ca": {
        "name": "Ford IAT2 (Method 2)",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:air-filter",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k222813": {
        "name": "Ford Front Driver Side Tire Pressure",
        "unit": "psi",
        "icon": "mdi:car-tire-alert",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k222814": {
        "name": "Ford Front Passenger Side Tire Pressure",
        "unit": "psi",
        "icon": "mdi:car-tire-alert",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k222815": {
        "name": "Ford Rear Driver Side Tire Pressure",
        "unit": "psi",
        "icon": "mdi:car-tire-alert",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "k222816": {
        "name": "Ford Rear Passenger Side Tire Pressure",
        "unit": "psi",
        "icon": "mdi:car-tire-alert",
        "device_class": SensorDeviceClass.PRESSURE,
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
