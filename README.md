# Home Assistant Torque OBD-II Integration
<p align="center">
  <img src="https://raw.githubusercontent.com/home-assistant/brands/refs/heads/master/custom_integrations/torque_logger/icon%402x.png" alt="Torque OBD Logo" width="125" />
  <img src="https://brands.home-assistant.io/_/torque/logo@2x.png" alt="Torque OBD Logo" width="300" />
</p>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JOHLC&repository=Home-Assistant-Torque-OBDII&category=Integration)
![Requires Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FJOHLC%2FHome-Assistant-Torque-OBDII%2Fmain%2Fhacs.json&query=%24.homeassistant&label=Requires%20Home%20Assistant&color=41BDF5&logo=homeassistant&logoColor=white)
![GitHub Release](https://img.shields.io/github/v/release/JOHLC/Home-Assistant-Torque-OBDII?color=blue&label=Release)
![GitHub Repo stars](https://img.shields.io/github/stars/JOHLC/Home-Assistant-Torque-OBDII)


[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JOHLC&repository=Home-Assistant-Torque-OBDII&category=Integration)

A Home Assistant custom integration for receiving vehicle telemetry from the Torque Android application and exposing it as sensors in Home Assistant.

**⚡️ Modern rewrite of the Torque logger integration for Home Assistant.**<br>

> **🤖 Disclosure: AI-Powered**<br>
> This integration is maintained and improved with the help of GitHub Copilot among various other AI assistants.<br>
> I am not a Python coder by any means. Community feedback, contributions, and code reviews are welcome!

## Overview

This custom integration receives vehicle telemetry data in Home Assistant. The data flows as follows:

**OBD-II adapter → Torque Android app → HTTP(S) upload → Home Assistant custom integration**

The Torque Android application connects to your vehicle's OBD-II port through a compatible adapter, collects vehicle parameters, and periodically uploads them to Home Assistant via an HTTP(S) endpoint. The integration converts those uploads into sensors you can use in automations, dashboards, and historical analysis.

This integration is **receive-only**. It cannot communicate back to the adapter, vehicle, or Torque app. It cannot send OBD-II or CAN bus commands, write ECU data, program modules, or control any vehicle function.

Bring your car's real-time OBD-II data into Home Assistant using the [Torque](https://torque-bhp.com/) Android app.<br>
This integration creates sensors for every OBD-II PID that your car reports, enabling automation, visualization, and monitoring of your vehicle.


## Features

- 🚗 **Real-time vehicle monitoring** - Get live data from your vehicle's OBD-II port
- 📊 **205+ vehicle parameters** - Speed, RPM, fuel level, temperatures, and more
- 🗺️ **GPS tracking** - Location, altitude, and bearing information
- 🔌 **Easy setup** - Simple UI-based configuration
- 📱 **Multiple vehicles** - Support for multiple cars with different email identifiers
- 🏠 **Home Assistant integration** - Works seamlessly with automations and dashboards

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

> **Home Assistant should be reachable from your phone** at the time Torque uploads data. Torque uploads periodically while it is running and connected. If the connection is unavailable, Torque may queue items (see **Web Upload Status**), but uploads are best-effort and some data may be dropped.

1. Open the **Torque** app on your Android device
2. Go to **Settings** → **Data Logging & Upload**
3. Configure:
   - **Web Upload URL**: Use your vehicle's unique endpoint.
     Examples:
     - **Local Home Assistant** (trusted private network):  
       `http://YOUR_HA_IP:8123/api/torque-2025-ford-escape`
     - **Remote Home Assistant with HTTPS**:  
       `https://YOUR_DOMAIN/api/torque-2025-ford-escape`
     > Use HTTPS for all remote access. **Do not transmit telemetry, credentials, or GPS data over unencrypted HTTP on public or untrusted networks.** Local HTTP is appropriate only on a trusted private network.
   - **Email Address**: Optional (Torque does not reliably send this field)
   - Enable logging
   - If you use **HTTPS**, prefer a reverse proxy on standard port **443** with a **publicly trusted certificate**. Torque may silently refuse self-signed or privately issued certificates even if the URL works in your browser.
4. **⚠️ IMPORTANT**: After configuring both Home Assistant and Torque for the first time:
   - Go to Android Settings → Apps → Torque (or Torque Pro)
   - Tap **Force Stop**
   - Reopen the app
   - Reconnect to your OBD-II adapter
5. Start driving!

**HTTPS troubleshooting note**: If a manual POST works but Torque's **Web Upload Status** shows queued items with **0 sent** and Home Assistant logs show nothing, the request is usually being blocked before it reaches Home Assistant. The most common cause is Torque not trusting the HTTPS certificate chain. Try a local `http://` URL for testing, or switch to HTTPS on port 443 with a certificate issued by a public CA such as Let's Encrypt.

**Note**: The integration domain is `torque_obd` to avoid conflicts with the built-in `torque` integration.

## Documentation

### 📚 Comprehensive Guides

- **[Setup Guide](custom_components/torque_obd/README.md)** - Detailed installation and configuration instructions
- **[PID Reference](PIDS.md)** - Complete database of 205+ supported OBD-II PIDs with descriptions
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions to common issues and problems
- **[Example Automations](examples/torque_configuration.yaml)** - Dashboard and automation examples
- **[Architecture Documentation](custom_components/torque_obd/ARCHITECTURE.md)** - Technical details for developers

### Quick Links

- [Supported Sensors](#supported-sensors)
- [Requirements](#requirements)
- [Example Use Cases](#example-use-cases)

## Supported Sensors

The integration **dynamically creates sensors** based on data received from Torque. Over **205+ PIDs** are supported:

- **Speed & Motion**: Vehicle speed, GPS speed, trip distance
- **Engine**: RPM, coolant temperature, oil temperature, intake air temperature
- **Fuel**: Fuel level, fuel consumption, fuel economy
- **Power**: Throttle position, engine load, battery voltage
- **Environment**: Ambient temperature, barometric pressure
- **GPS**: Latitude, longitude, altitude, bearing
- And many more OBD-II parameters

📖 **[View Complete PID Database](PIDS.md)** - Detailed reference of all 205+ supported sensors with descriptions, units, and compatibility information.

**Sensor Names**: The integration automatically uses sensor names provided by Torque, giving you accurate, vehicle-specific names for each parameter.

**Entity IDs**: All sensors are prefixed with your vehicle name (e.g., `sensor.2025_ford_escape_fuel_level`) for easy identification.

**Note on Units**: Torque sends sensor values in **metric units only** (°C, km/h, km, L, kPa) regardless of app settings. Home Assistant will convert these based on your unit system preferences.

## Requirements

- Home Assistant (2023.1 or later recommended)
- Torque Android app with web upload support (see note below)
- OBD-II adapter compatible with your vehicle and Torque
- Vehicle with OBD-II port (most cars 1996+)

> **Torque version note**: Web upload has been confirmed with **Torque Pro**. Whether **Torque Lite** (the free version) supports web upload has not been independently verified. If you are using Torque Lite and it works, please open an issue to share your experience.

> **Adapter compatibility note**: Adapter compatibility, connection type (Bluetooth, BLE, Wi-Fi, or wired), and vehicle PID availability are determined by Torque, the adapter, and the vehicle—not by this integration. Refer to Torque's documentation and your adapter's specifications for compatibility details.

## Security Considerations

This integration is **receive-only**.

- It does not communicate directly with your vehicle or OBD-II adapter.
- It does not send commands to the vehicle.
- It cannot modify ECU data, program modules, change odometer values, or interact with CAN bus functions.
- It only processes telemetry uploaded by the Torque application.

For remote access, follow standard Home Assistant security practices:

- Use HTTPS for all remote access.
- **Do not transmit telemetry, credentials, or GPS data over unencrypted HTTP on public or untrusted networks.**
- Avoid exposing Home Assistant directly to the internet without proper authentication and security controls.
- Keep Home Assistant and installed integrations up to date.
- Only expose the data and sensors you are comfortable storing in Home Assistant.

## Privacy Considerations

This integration can receive and store sensitive telemetry, including:

- **GPS location history**: Latitude, longitude, altitude, and bearing are logged continuously while driving. Anyone with access to your Home Assistant instance can view your location history.
- **Trip data**: Trip distances, times, and driving patterns are recorded.
- **Vehicle identifiers**: The vehicle name you configure and any email identifier are stored in Home Assistant.
- **Driving behavior**: Speed, acceleration, engine load, and other parameters can reveal driving habits.

Recommendations:

- Store only the sensors you need; remove sensors that expose more data than intended.
- Restrict access to Home Assistant to trusted users.
- Review Home Assistant's data retention settings for long-term history.
- Be aware that GPS and trip data uploaded over the internet traverses your network; use HTTPS to encrypt it in transit.

This integration is intended for telemetry, dashboards, history, and automations. It is not a replacement for your vehicle's instrument cluster, professional diagnostic equipment, or safety systems.

> **Timestamps**: Home Assistant timestamps represent when data was **received** by the integration, not necessarily when the vehicle measurement occurred. Network latency and Torque's logging interval introduce a small delay (typically 1–6 seconds).

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

This integration works with the [Torque](https://torque-bhp.com/) Android application by Ian Hawkins.
