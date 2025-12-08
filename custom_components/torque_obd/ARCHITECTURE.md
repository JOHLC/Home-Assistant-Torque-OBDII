# Torque OBD-II Integration Architecture

## Overview

This document describes how the Torque OBD-II integration works internally.

## Architecture Diagram

```
┌─────────────────────┐
│   Torque Pro App    │
│   (Android Phone)   │
│                     │
│  Connected to car   │
│  via OBD-II adapter │
└──────────┬──────────┘
           │ HTTP POST/GET
           │ Vehicle data
           ▼
┌─────────────────────────────────────┐
│  Home Assistant                     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ /api/torque-2025-ford-escape│   │ ◄─── Unique HTTP endpoint per vehicle
│  │ /api/torque-2017-ford-fusion│   │      (no auth)
│  │  HTTP Views                  │   │
│  └───────────┬──────────────────┘   │
│              │                      │
│              ▼                      │
│  ┌─────────────────────────────┐   │
│  │  TorqueView (per vehicle)   │   │ ◄─── Receives data
│  │  Handler                    │   │      Processes all incoming data
│  └───────────┬──────────────────┘   │
│              │                      │
│              │ dispatcher_send()    │
│              ▼                      │
│  ┌─────────────────────────────┐   │
│  │    Sensors (per vehicle)    │   │ ◄─── 26 sensor entities per vehicle
│  │  (TorqueSensor)             │   │     Update their state
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Config Flow                │   │ ◄─── UI configuration
│  │                             │   │      Stores vehicle name
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

## Data Flow

1. **Vehicle Data Collection**
   - Torque Pro app connects to car's OBD-II port via Bluetooth/WiFi adapter
   - App collects vehicle parameters (speed, RPM, temperature, etc.)
   - Data is sent periodically to configured URL

2. **HTTP Request to Home Assistant**
   - Torque sends HTTP POST or GET request to vehicle-specific endpoint (e.g., `/api/torque-2025-ford-escape`)
   - Request contains form data with vehicle parameters:
     - `eml`: Email identifier
     - `k5`: Vehicle speed
     - `kc`: Engine RPM
     - `k2f`: Fuel level
     - And many more PIDs...

3. **Data Reception & Routing**
   - `TorqueView` for that specific vehicle receives the HTTP request
   - Processes all incoming data without email validation (Torque does not reliably send email)
   - Stores data in `hass.data`

4. **Sensor Updates**
   - `async_dispatcher_send()` notifies all sensors for this vehicle
   - Each sensor checks if its PID key is in the data
   - Sensors update their state with new values
   - Home Assistant UI reflects the changes

5. **Integration Lifecycle**
   - Setup: Creates unique HTTP view per vehicle, loads sensors
   - Runtime: Receives data on vehicle-specific endpoints, updates sensors
   - Unload: Cleans up sensors, removes entry data

## File Structure

```
custom_components/torque_obd/
├── __init__.py          # Main integration setup, HTTP view
├── config_flow.py       # UI configuration flow
├── const.py             # Constants and sensor definitions
├── sensor.py            # Sensor entities implementation
├── manifest.json        # Integration metadata
├── strings.json         # UI strings for config flow
└── README.md           # User documentation
```

## Key Components

### __init__.py

- **Purpose**: Integration entry point and HTTP endpoint
- **Key Classes**:
  - `TorqueView`: Handles HTTP requests from Torque app
- **Key Functions**:
  - `async_setup_entry()`: Sets up integration instance
  - `async_unload_entry()`: Cleans up on removal

### sensor.py

- **Purpose**: Defines vehicle sensor entities
- **Key Classes**:
  - `TorqueSensor`: Base sensor class for all vehicle parameters
- **Features**:
  - Automatic state updates via dispatcher
  - Device info grouping
  - Unit of measurement
  - Device class assignment

### config_flow.py

- **Purpose**: UI-based configuration
- **Key Classes**:
  - `TorqueConfigFlow`: Handles integration setup wizard
- **Features**:
  - Vehicle name input and validation
  - Email validation
  - Unique ID enforcement
  - User-friendly error messages
  - Creates URL-safe endpoint names

### const.py

- **Purpose**: Central configuration and definitions
- **Key Constants**:
  - `SENSOR_DEFINITIONS`: Default PID-to-sensor mappings
  - `SENSOR_DEFINITIONS_FILE`: Name of custom sensor definitions file
  - `DOMAIN`: Integration domain name (`torque_obd`)
  - `CONF_VEHICLE_NAME`: Vehicle name configuration key
  - `CONF_EMAIL`: Email configuration key
- **Key Functions**:
  - `load_sensor_definitions()`: Loads and merges default and custom sensor definitions

## Sensor Definition Loading

At integration startup, sensor definitions are loaded in the following order:

1. **Default Definitions**: Built-in `SENSOR_DEFINITIONS` dictionary in `const.py`
2. **Custom Definitions**: Optional `torque_sensor_definitions.yaml` in config directory
3. **Merging**: Custom definitions override defaults, new PIDs are added
4. **Storage**: Merged definitions stored in `hass.data[DOMAIN]["sensor_definitions"]`
5. **Usage**: Dynamic sensor creation uses merged definitions

This allows users to:
- Override default sensor names, units, or icons
- Fix incorrect PID mappings for their specific setup
- Add support for custom PIDs not in the default list

Example custom sensor definition file location:
```
/config/torque_sensor_definitions.yaml
```

## Configuration Storage

Configuration is stored as a config entry with:
- **Entry ID**: Unique identifier for this vehicle
- **Data**: `{ "vehicle_name": "2025 Ford Escape", "email": "" }` (email is optional)
- **Runtime Data**: Latest vehicle data, API path, and sensors

## Security Considerations

- HTTP endpoints are **not authenticated** (Torque limitation)
- Each vehicle has its own unique endpoint
- Vehicle name must be unique to prevent endpoint conflicts
- Recommended for use on trusted local networks only
- See README.md security section for mitigation strategies

## Multiple Vehicle Support

The integration supports multiple vehicles:
1. Each vehicle configured with unique vehicle name
2. Each vehicle gets its own unique HTTP endpoint (e.g., `/api/torque-2025-ford-escape`)
3. Data is routed by endpoint URL, not by email (Torque does not reliably send email)
4. Each vehicle gets its own set of 26 sensors
5. Devices grouped by vehicle name in UI
6. No data conflicts between vehicles

## State Management

Sensor states are managed through:
- **Dispatcher pattern**: Central notification of updates
- **Callback registration**: Sensors subscribe to updates
- **State class**: Proper measurement/total_increasing classification
- **Device class**: Semantic meaning (temperature, voltage, etc.)

## Extension Points

To add new sensors:
1. Add PID key and definition to `SENSOR_DEFINITIONS` in `const.py`
2. Sensors are automatically created from definitions
3. No changes needed to `sensor.py` or other files

To modify data handling:
1. Edit `_handle_request()` in `TorqueView` class
2. Add custom processing before dispatcher send
3. Store additional data in `hass.data[DOMAIN][entry_id]`
