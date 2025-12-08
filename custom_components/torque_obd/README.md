# Torque OBD-II Integration for Home Assistant

This integration allows Home Assistant to receive vehicle data from the [Torque Pro](https://torque-bhp.com/) Android application via OBD-II.

## Features

- Real-time vehicle data monitoring
- Support for 30+ vehicle parameters including:
  - Vehicle speed and GPS speed
  - Engine RPM
  - Engine coolant, oil, and intake air temperatures
  - Fuel level and consumption
  - Throttle position and engine load
  - Battery voltage
  - GPS location data (latitude, longitude, altitude, bearing)
  - Trip distance and time
  - And many more OBD-II parameters

## Installation

1. Copy the `torque_obd` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration → Integrations
4. Click the "+ ADD INTEGRATION" button
5. Search for "Torque OBD-II"
6. Follow the configuration steps

## Configuration

### Home Assistant Setup

1. Add the Torque OBD-II integration through the UI
2. Enter a descriptive **Vehicle Name** (e.g., "2025 Ford Escape" or "2017 Ford Fusion")
3. Optionally enter an **Email Address** (note: Torque does not reliably send email in payloads, so this is optional)
4. Home Assistant will create a unique API endpoint for this vehicle based on the name

### Torque App Setup

Each vehicle gets its own unique API endpoint based on the vehicle name you configured.

**Example**: If you named your vehicle "2025 Ford Escape", the endpoint will be:
`http://YOUR_HA_IP:8123/api/torque-2025-ford-escape`

**Example**: If you named your vehicle "2017 Ford Fusion", the endpoint will be:
`http://YOUR_HA_IP:8123/api/torque-2017-ford-fusion`

#### Configuration Steps:

1. Open Torque Pro on your Android device
2. Go to Settings → Data Logging & Upload
3. Select "Webserver" or "Web Upload"
4. Configure the following:
   - **Web Upload URL**: Use the unique endpoint shown in Home Assistant after configuration
   - **Email Address**: Optional (Torque does not reliably send this field)
   - **Enable Logging**: Turn on
5. Select the PIDs you want to log
6. Save settings

**Note**: Replace `YOUR_HA_IP` with your Home Assistant IP address. If using HTTPS, use `https://` instead.

### Finding Your Vehicle's API Endpoint

After configuring a vehicle in Home Assistant:
1. Go to Configuration → Integrations
2. Find your Torque OBD-II vehicle entry
3. The API endpoint will be shown in the integration details or check the logs

The endpoint format is: `/api/torque-<vehicle-name-in-lowercase-with-dashes>`

### Example URL Configuration

For a vehicle named "2025 Ford Escape":
```
http://192.168.1.100:8123/api/torque-2025-ford-escape
```

For a vehicle named "2017 Ford Fusion":
```
http://192.168.1.100:8123/api/torque-2017-ford-fusion
```

Or if using SSL:
```
https://your-domain.com/api/torque-2025-ford-escape
```

## Sensors

The integration automatically creates sensors for all supported vehicle parameters. Each sensor will update when new data is received from the Torque app.

**Important Note on Units**: Torque Pro typically sends all sensor values in metric units, regardless of the unit settings in the app. This means:
- Temperatures are in Celsius (°C)
- Speeds are in kilometers per hour (km/h)
- Distances are in kilometers (km)
- Fuel volumes are in liters (L)
- Pressures are in kilopascals (kPa)

The integration defines these units in the sensor definitions and Home Assistant will handle any necessary conversions based on your Home Assistant unit system preferences.

### Custom Sensor Definitions

You can customize sensor definitions or add support for custom PIDs by creating a `torque_sensor_definitions.yaml` file in your Home Assistant configuration directory.

#### Creating Custom Sensor Definitions

1. Create a file named `torque_sensor_definitions.yaml` in your Home Assistant config directory (same location as `configuration.yaml`)
2. Add your custom sensor definitions in YAML format
3. Restart Home Assistant to load the new definitions

#### YAML File Format

```yaml
# Override an existing sensor
kd:
  name: "My Car Speed"
  unit: "km/h"
  icon: "mdi:speedometer"
  device_class: null
  state_class: "measurement"

# Add a custom sensor for a new PID
kff5001:
  name: "Custom Boost Pressure"
  unit: "psi"
  icon: "mdi:gauge"
  device_class: "pressure"
  state_class: "measurement"
```

#### Sensor Definition Fields

- **name** (required): Human-readable name for the sensor
- **unit** (optional): Unit of measurement (e.g., "km/h", "°C", "RPM", "%")
- **icon** (optional): Material Design Icon name (e.g., "mdi:speedometer"). Defaults to "mdi:car-info"
- **device_class** (optional): Home Assistant device class (e.g., "temperature", "voltage", "pressure", null)
- **state_class** (optional): Home Assistant state class:
  - `"measurement"`: For values that can go up or down
  - `"total_increasing"`: For monotonically increasing values (like trip distance)
  - `null`: For values without a state class

#### PID Naming Convention

Torque uses the following PID naming convention:

**Standard OBD-II PIDs**: "k" + hex value
- `k4`: Engine Load (OBD-II PID 0x04)
- `k5`: Engine Coolant Temperature (OBD-II PID 0x05)
- `kc`: Engine RPM (OBD-II PID 0x0C)
- `kd`: Vehicle Speed (OBD-II PID 0x0D)
- `kf`: Intake Air Temperature (OBD-II PID 0x0F)
- `k10`: MAF Air Flow Rate (OBD-II PID 0x10)
- `k11`: Throttle Position (OBD-II PID 0x11)
- `k2f`: Fuel Level (OBD-II PID 0x2F)

**Torque Custom PIDs**: "kff" + number
- `kff1001`: GPS Latitude
- `kff1002`: GPS Longitude
- `kff1006`: GPS Speed
- `kff1238`: Battery Voltage
- `kff1266`: Trip Distance

#### Example Configuration File

An example configuration file is included in the integration: `torque_sensor_definitions.yaml.example`. Copy this file to your config directory and modify it to suit your needs:

```bash
cp custom_components/torque_obd/torque_sensor_definitions.yaml.example /config/torque_sensor_definitions.yaml
```

#### How It Works

1. The integration loads default sensor definitions at startup
2. If `torque_sensor_definitions.yaml` exists in your config directory, it loads the custom definitions
3. Custom definitions **override** default definitions for the same PID
4. New PIDs in the custom file are **added** to the available sensors
5. Any PIDs received from Torque that aren't in either file will create a generic sensor automatically

### Supported Sensors

- **Speed**: Vehicle speed (OBD-II), GPS speed
- **Engine**: RPM, coolant temperature, oil temperature, intake air temperature
- **Fuel**: Fuel level, fuel remaining, fuel used (trip), average fuel economy, instant fuel economy
- **Throttle & Load**: Throttle position, engine load
- **Battery**: Battery voltage
- **GPS**: Latitude, longitude, altitude, bearing
- **Distance & Time**: Trip distance, trip time
- **Other**: Ambient air temperature, MAF air flow rate, timing advance, barometric pressure, fuel pressure, intake manifold pressure

## Security Considerations

The integration creates vehicle-specific HTTP endpoints (e.g., `/api/torque-<vehicle-name>`) that **do not require authentication**. This is necessary because the Torque app does not support authenticated requests. To mitigate security risks:

1. **Network Security**: Use this integration only on a trusted local network
2. **Email Identifier**: Data is filtered by email address - only configured vehicles will have their data stored
3. **Firewall**: Consider using firewall rules to restrict access to the Home Assistant instance
4. **Internal Network**: For best security, keep Home Assistant on an internal network and use a VPN for remote access

If you need to expose Home Assistant externally, consider using:
- A reverse proxy with additional authentication
- Network segmentation to isolate the Home Assistant instance
- VPN access instead of direct internet exposure

## Troubleshooting

### No Data Appearing in Home Assistant

1. **Check the Torque app is sending data**:
   - Ensure "Enable Logging" is turned on
   - Verify the URL is correct (including port 8123)
   - Check your device has network connectivity

2. **Check Home Assistant logs**:
   - Go to Configuration → Logs
   - Look for errors related to "torque"

3. **Verify endpoint URL**:
   - Make sure the Torque app URL matches your vehicle's unique endpoint
   - Check for typos in the vehicle name portion of the URL

4. **Network connectivity**:
   - Ensure your Android device can reach Home Assistant
   - Try accessing `http://YOUR_HA_IP:8123` in a browser on your Android device
   - Check firewall settings

### Sensors Show "Unavailable"

- Sensors will show as "Unavailable" until the first data is received from Torque
- Start driving with the Torque app running and logging enabled
- Data should appear within a few seconds once logging starts

## Technical Details

### API Endpoints

Each configured vehicle gets its own unique HTTP endpoint at `/api/torque-<vehicle-name>` that accepts both GET and POST requests with form data containing OBD-II parameters.

The endpoint is created automatically when you configure a vehicle, using the vehicle name you provide (converted to lowercase with spaces replaced by dashes).

**Examples**:
- Vehicle "2025 Ford Escape" → `/api/torque-2025-ford-escape`
- Vehicle "2017 Ford Fusion" → `/api/torque-2017-ford-fusion`
- Vehicle "My Car" → `/api/torque-my-car`

### Data Format

Torque sends data using parameter keys like:
- `k5`: Vehicle speed
- `kc`: Engine RPM
- `k2f`: Fuel level
- `kff1006`: GPS speed
- And many more...

The integration automatically maps these keys to human-readable sensor names.

### Multiple Vehicles

You can add multiple vehicles by creating additional integration instances with different vehicle names and email addresses. Each vehicle will have:
- Its own unique API endpoint
- Its own set of sensors
- Its own device in Home Assistant

This allows you to monitor multiple vehicles simultaneously without any conflicts.

## Credits

This integration receives data from the Torque Pro Android application. Torque is a trademark of Ian Hawkins.

## License

This integration is provided as-is under the MIT License.
