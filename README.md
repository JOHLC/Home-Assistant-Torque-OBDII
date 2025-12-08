# Home Assistant Torque OBD-II Integration

[![Validate with hassfest](https://github.com/JOHLC/Home-Assistant-Torque-OBDII/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/JOHLC/Home-Assistant-Torque-OBDII/actions)

A fully functional Home Assistant custom integration for receiving vehicle data from the Torque Pro Android application via OBD-II.

## Overview

This integration allows you to monitor real-time vehicle diagnostics data from your car's OBD-II port directly in Home Assistant. The Torque Pro Android app collects data from your vehicle and sends it to Home Assistant via HTTP, where it's converted into sensors you can use in automations, dashboards, and more.

## Features

- 🚗 **Real-time vehicle monitoring** - Get live data from your vehicle's OBD-II port
- 📊 **30+ vehicle parameters** - Speed, RPM, fuel level, temperatures, and more
- 🗺️ **GPS tracking** - Location, altitude, and bearing information
- 🔌 **Easy setup** - Simple UI-based configuration
- 📱 **Multiple vehicles** - Support for multiple cars with different email identifiers
- 🏠 **Native Home Assistant integration** - Works seamlessly with automations and dashboards

## Quick Start

### Installation

#### Option 1: HACS (Recommended)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

1. Open HACS in your Home Assistant instance
2. Click on **Integrations**
3. Click the **⋮** menu in the top right corner
4. Select **Custom repositories**
5. Add this repository URL: `https://github.com/JOHLC/Home-Assistant-Torque-OBDII`
6. Select **Integration** as the category
7. Click **Add**
8. Search for **Torque OBD-II** in HACS
9. Click **Download**
10. Restart Home Assistant
11. Go to **Configuration** → **Integrations**
12. Click **+ ADD INTEGRATION**
13. Search for **Torque OBD-II**
14. Enter your vehicle's name (e.g., "2025 Ford Escape")
15. Optionally enter an email (note: Torque does not reliably send this)
16. Note the unique API endpoint created for your vehicle

#### Option 2: Manual Installation

1. Copy the `custom_components/torque_obd` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Configuration** → **Integrations**
4. Click **+ ADD INTEGRATION**
5. Search for **Torque OBD-II**
6. Enter your vehicle's name (e.g., "2025 Ford Escape")
7. Optionally enter an email (note: Torque does not reliably send this)
8. Note the unique API endpoint created for your vehicle

### Torque App Configuration

Each vehicle gets its own unique API endpoint based on the name you configured.

1. Open **Torque Pro** on your Android device
2. Go to **Settings** → **Data Logging & Upload**
3. Configure:
   - **Web Upload URL**: Use your vehicle's unique endpoint (e.g., `http://YOUR_HA_IP:8123/api/torque-2025-ford-escape`)
   - **Email Address**: Optional (Torque does not reliably send this field)
   - Enable logging
4. Start driving!

**Note**: The integration domain is `torque_obd` to avoid conflicts with the native Torque integration.

## Documentation

For detailed setup instructions, troubleshooting, and sensor information, see the [Torque integration README](custom_components/torque_obd/README.md).

For example automations and dashboard configurations, see the [example configuration file](examples/torque_configuration.yaml).

## Supported Sensors

The integration **dynamically creates sensors** based on data received from Torque:

- **Speed & Motion**: Vehicle speed, GPS speed, trip distance
- **Engine**: RPM, coolant temperature, oil temperature, intake air temperature
- **Fuel**: Fuel level, fuel consumption, fuel economy
- **Power**: Throttle position, engine load, battery voltage
- **Environment**: Ambient temperature, barometric pressure
- **GPS**: Latitude, longitude, altitude, bearing
- And many more OBD-II parameters

**Sensor Names**: The integration automatically uses sensor names provided by Torque, giving you accurate, vehicle-specific names for each parameter.

**Entity IDs**: All sensors are prefixed with your vehicle name (e.g., `sensor.2025_ford_escape_fuel_level`) for easy identification.

**Note on Units**: Torque sends sensor values in **metric units only** (°C, km/h, km, L, kPa) regardless of app settings. Home Assistant will convert these based on your unit system preferences.

## Requirements

- Home Assistant (2023.1 or later recommended)
- Torque Pro Android app
- OBD-II adapter (Bluetooth or WiFi)
- Vehicle with OBD-II port (most cars 1996+)

## Example Use Cases

- Track fuel efficiency over time
- Monitor engine health with temperature sensors
- Create automations based on vehicle location
- Log trip data for expense tracking
- Alert on low fuel or battery voltage
- Display vehicle stats on your dashboard

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

This integration works with the [Torque Pro](https://torque-bhp.com/) Android application by Ian Hawkins.
