# Troubleshooting Guide

This guide helps you resolve common issues with the Torque OBD-II integration for Home Assistant.

## Table of Contents

- [Quick Checklist](#quick-checklist)
- [Common Issues](#common-issues)
  - [No Data Appearing in Home Assistant](#no-data-appearing-in-home-assistant)
  - [Sensors Show "Unavailable"](#sensors-show-unavailable)
  - [Connection Issues](#connection-issues)
  - [Wrong or Missing Sensors](#wrong-or-missing-sensors)
  - [Data is Incorrect or Inaccurate](#data-is-incorrect-or-inaccurate)
  - [Multiple Vehicles Not Working](#multiple-vehicles-not-working)
- [Configuration Validation](#configuration-validation)
- [Network Troubleshooting](#network-troubleshooting)
- [Debugging](#debugging)
- [Getting Help](#getting-help)

## Quick Checklist

Before diving into detailed troubleshooting, verify these basics:

- [ ] **Home Assistant** integration is installed and configured
- [ ] **Torque Pro** app is purchased and installed (free version doesn't support data upload)
- [ ] **OBD-II adapter** is connected to vehicle and paired with phone
- [ ] **Vehicle ignition** is on (engine doesn't need to be running for most sensors)
- [ ] **Torque app** is running and connected to OBD adapter
- [ ] **Data logging** is enabled in Torque settings
- [ ] **Web upload URL** in Torque is correctly configured
- [ ] **Network connectivity** between phone and Home Assistant is working
- [ ] **After initial setup**: Torque app has been **force stopped and reopened**

## Common Issues

### No Data Appearing in Home Assistant

**Symptom**: Integration is configured but no sensor entities appear or all show "Unknown".

#### Solution 1: Force Stop and Restart Torque App

🔴 **CRITICAL**: After configuring both Home Assistant and Torque for the first time, you **must** force stop the Torque app and reopen it.

**Steps**:
1. Go to Android Settings → Apps → Torque Pro
2. Tap "Force Stop"
3. Reopen Torque Pro
4. Reconnect to your OBD-II adapter
5. Start driving or let the engine idle for 30 seconds

**Why**: Torque caches certain settings and may not immediately start sending data to the new endpoint until fully restarted.

#### Solution 2: Verify Torque Configuration

1. Open **Torque Pro** app
2. Go to **Settings** → **Data Logging & Upload**
3. Verify these settings:
   - **Webserver URL**: Should be `http://YOUR_HA_IP:8123/api/torque-your-vehicle-name`
   - **Log to Webserver**: Should be **enabled** (checkbox checked)
   - **Logging Interval**: Default is usually 1-5 seconds
   - **Select what to log**: At least some PIDs should be selected

4. **Test the connection**:
   - In Torque, there's usually a "Test" button near the webserver settings
   - This should return a success message if Home Assistant is reachable

#### Solution 3: Check Home Assistant Logs

1. Go to **Settings** → **System** → **Logs**
2. Search for "torque"
3. Look for any error messages such as:
   - Connection errors
   - Invalid data format errors
   - Permission errors

**Common log entries**:
- ✅ Good: `Received data for vehicle: 2025 Ford Escape`
- ❌ Problem: `No data received from Torque`
- ❌ Problem: `Invalid URL format`

#### Solution 4: Verify Network Connectivity

From your Android device:
1. Open a web browser
2. Navigate to: `http://YOUR_HA_IP:8123`
3. You should see the Home Assistant login page

If you can't reach Home Assistant:
- Check your phone is on the same WiFi network
- Check firewall settings on Home Assistant server
- Try using the IP address instead of hostname
- Check if Home Assistant is behind a reverse proxy

#### Solution 5: Check Sensor Selection in Torque

1. Open **Torque Pro**
2. Go to **Settings** → **Data Logging & Upload**
3. Tap **Select what to log**
4. Ensure some PIDs are checked (green checkmarks)
5. Common essential PIDs to select:
   - Vehicle Speed (OBD)
   - Engine RPM
   - Fuel Level
   - Coolant Temperature

#### Solution 6: Test with Manual Request

Test if Home Assistant is receiving requests:

```bash
# From your computer or Android device (using Termux or similar)
curl -X POST \
  http://YOUR_HA_IP:8123/api/torque-your-vehicle-name \
  -d "eml=test@test.com&k05=75&k0c=2000&k0d=50"
```

Check Home Assistant logs for activity after running this command.

### Sensors Show "Unavailable"

**Symptom**: Sensor entities exist but show as "Unavailable" or "Unknown".

#### Solution 1: Start Driving

Many sensors only report data when:
- Engine is running
- Vehicle is in motion
- Specific conditions are met (e.g., A/C on for A/C pressure sensors)

**Try**: Start the engine and drive for 1-2 minutes.

#### Solution 2: Check OBD-II Adapter Connection

1. Open Torque app
2. Check the status bar at the top
3. Should show "Connected" with adapter name
4. If not connected:
   - Check Bluetooth pairing
   - Check adapter is plugged into OBD-II port
   - Try reconnecting in Torque settings

#### Solution 3: Vehicle Compatibility

Not all vehicles support all PIDs. Your vehicle may not support certain sensors:

- Older vehicles (pre-2000) have fewer sensors
- Some manufacturers don't provide certain data
- Diesel engines may have different sensors than gas engines

**Check**: Look at which sensors ARE working to confirm basic connectivity.

#### Solution 4: Check Logging Interval

If the logging interval is too long, sensors may appear unavailable:

1. Torque → Settings → Data Logging & Upload
2. Check **Logging Interval**
3. Try setting it to 1-2 seconds for testing

### Connection Issues

**Symptom**: Torque can't connect to Home Assistant endpoint.

#### Issue: Wrong URL Format

✅ **Correct formats**:
```
http://192.168.1.100:8123/api/torque-2025-ford-escape
https://homeassistant.local:8123/api/torque-my-car
```

❌ **Incorrect formats**:
```
http://192.168.1.100:8123/api/torque_obd/2025-ford-escape  # Wrong path
http://192.168.1.100/api/torque-2025-ford-escape  # Missing port
https://192.168.1.100:8123/api/torque-2025-ford-escape  # HTTP vs HTTPS mismatch
192.168.1.100:8123/api/torque-2025-ford-escape  # Missing http://
```

**Note**: The vehicle name portion is converted to lowercase with spaces replaced by dashes.

#### Issue: SSL/HTTPS Problems

If using HTTPS with self-signed certificates:

**Option 1**: Use HTTP instead (if on local network)
```
http://192.168.1.100:8123/api/torque-2025-ford-escape
```

**Option 2**: Install certificate on Android device
1. Export Home Assistant SSL certificate
2. Install on Android: Settings → Security → Install certificate
3. Restart Torque app

#### Issue: Port Forwarding

If accessing Home Assistant remotely:
- Ensure port 8123 (or your custom port) is forwarded
- Consider security implications (see Security section)
- Use VPN instead of direct port forwarding for better security

#### Issue: Reverse Proxy Configuration

If using Nginx, Traefik, or similar:
- Ensure `/api/torque-*` paths are properly proxied
- Check that request headers are passed through
- Verify POST requests are allowed

Example Nginx configuration:
```nginx
location /api/ {
    proxy_pass http://homeassistant:8123;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Wrong or Missing Sensors

**Symptom**: Expected sensors don't appear, or sensor names are wrong.

#### Solution 1: Check PID Selection in Torque

Only PIDs selected in Torque will send data:

1. Torque → Settings → Data Logging & Upload
2. Tap **Select what to log**
3. Enable the sensors you want
4. Force stop and restart Torque app

#### Solution 2: Verify PID Support

Not all vehicles support all PIDs. Check the [PID Reference Guide](PIDS.md) to see which PIDs are supported.

**Test a specific PID**:
1. In Torque, go to Realtime Information screen
2. Add a dashboard widget for the sensor
3. If it shows "---" or doesn't update, your vehicle doesn't support that PID

#### Solution 3: Custom Sensor Definitions

If sensor names are wrong, you can customize them:

1. Create file: `/config/torque_sensor_definitions.yaml`
2. Add your custom definitions:

```yaml
k05:
  name: "Engine Coolant Temp"
  unit: "°C"
  icon: "mdi:thermometer"
  device_class: "temperature"
  state_class: "measurement"
```

3. Restart Home Assistant

See [Custom Sensor Definitions](custom_components/torque_obd/README.md#custom-sensor-definitions-optional) for details.

#### Solution 4: Dynamic Sensor Creation

Remember that sensors are created **dynamically** when data is received:
- Drive the vehicle for 2-3 minutes
- Check sensors again after driving
- Some sensors only appear under specific conditions (e.g., A/C on, turbo spooling)

### Data is Incorrect or Inaccurate

**Symptom**: Sensor values seem wrong or don't match Torque app display.

#### Issue: Unit Mismatch

**Important**: Torque sends data in **metric units only**, regardless of display settings:

| Type | Torque Sends | Home Assistant Converts |
|------|--------------|-------------------------|
| Temperature | Always °C | To °F if you use Imperial |
| Speed | Always km/h | To mph if you use Imperial |
| Distance | Always km | To miles if you use Imperial |
| Volume | Always liters | To gallons if you use Imperial |
| Pressure | Always kPa | To psi based on device class |

**Check your Home Assistant unit system**:
1. Settings → System → General
2. Look at "Unit System"
3. This affects how values are displayed, not how they're stored

#### Issue: OBD Adapter Calibration

Some adapters report incorrect voltage:
- **kff1238** (Adapter voltage) may differ from actual battery voltage
- **k42** (Control module voltage) is usually more accurate
- Voltage difference of 0.1-0.3V is normal due to cable resistance

#### Issue: GPS Accuracy

GPS data from phone may be inaccurate:
- Ensure GPS is enabled on Android device
- Give GPS time to acquire satellites (1-2 minutes outdoors)
- GPS accuracy improves with more satellites visible
- Buildings and tunnels affect GPS accuracy

**Check GPS status**: 
- **kff123a** shows number of satellites
- **kff1239** shows GPS accuracy in meters
- 8+ satellites and <10m accuracy is good

#### Issue: Calculated Values

Some Torque PIDs are calculated and may not be accurate:
- **kff1201/kff1203/kff1207**: Fuel economy calculations
- **kff1225**: Torque calculations
- **kff1226/kff1273**: Horsepower/kW calculations
- **kff126a**: Distance to empty estimates

These depend on vehicle profile settings in Torque and may not match actual values.

#### Issue: Sensor Lag

There can be delay between real-time and Home Assistant:
- Network latency (usually <1 second)
- Logging interval in Torque (default 1-5 seconds)
- Home Assistant processing time (<1 second)

Total lag is typically 2-6 seconds, which is normal.

### Multiple Vehicles Not Working

**Symptom**: Second or third vehicle doesn't work, or data mixes between vehicles.

#### Solution 1: Verify Unique Vehicle Names

Each vehicle **must** have a unique name in Home Assistant:

✅ Good:
- Vehicle 1: "2025 Ford Escape"
- Vehicle 2: "2017 Ford Fusion"

❌ Bad:
- Vehicle 1: "My Car"
- Vehicle 2: "My Car" (duplicate!)

#### Solution 2: Check Unique Endpoints

Each vehicle gets its own endpoint. Verify in integration config:
- Vehicle 1: `/api/torque-2025-ford-escape`
- Vehicle 2: `/api/torque-2017-ford-fusion`

#### Solution 3: Use Different Torque Profiles

If using multiple vehicles with one phone:
1. Create separate vehicle profiles in Torque
2. Each profile should have its own web upload URL
3. Switch profiles in Torque when changing vehicles

#### Solution 4: Verify Email Identifiers (Optional)

While email is optional, it can help with identification:
- Vehicle 1 email: `car1@example.com`
- Vehicle 2 email: `car2@example.com`

**Note**: Torque doesn't reliably send email, so the integration doesn't enforce it.

## Configuration Validation

### Verify Integration Setup

1. Go to **Settings** → **Devices & Services**
2. Find **Torque OBD-II** integration
3. Click on it to see configured vehicles
4. Each vehicle should show:
   - Vehicle name
   - Number of entities (sensors)
   - Status (should not show errors)

### Verify Endpoint URL

The integration creates endpoints in this format:
```
/api/torque-{vehicle-name-slug}
```

Where `{vehicle-name-slug}` is your vehicle name:
- Converted to lowercase
- Spaces replaced with hyphens
- Special characters removed

**Examples**:
- "2025 Ford Escape" → `/api/torque-2025-ford-escape`
- "My Car!" → `/api/torque-my-car`
- "Mom's Honda" → `/api/torque-moms-honda`

**Find your endpoint**:
1. Check Home Assistant logs after integration setup
2. Or look in `.storage/core.config_entries` (advanced)
3. Or check integration configuration in the UI

### Verify Sensor Entities

1. Go to **Settings** → **Devices & Services**
2. Click on **Torque OBD-II** integration
3. Click on your vehicle
4. You should see sensor entities listed
5. Click on a sensor to see its state and history

**Entity ID format**:
```
sensor.{vehicle_name}_{sensor_name}
```

**Examples**:
- `sensor.2025_ford_escape_fuel_level`
- `sensor.2025_ford_escape_engine_rpm`
- `sensor.2025_ford_escape_vehicle_speed`

## Network Troubleshooting

### Test Home Assistant Accessibility

**From Android device (using a browser)**:
1. Navigate to: `http://YOUR_HA_IP:8123`
2. Should see Home Assistant login page
3. If not, check network settings

**Common network issues**:
- Phone on different WiFi network (e.g., guest network)
- WiFi isolation enabled (AP isolation)
- Firewall blocking port 8123
- Home Assistant not binding to correct network interface

### Test with cURL (Advanced)

From a computer on the same network:

```bash
# Test if endpoint exists
curl -I http://YOUR_HA_IP:8123/api/torque-your-vehicle-name

# Expected response:
# HTTP/1.1 405 Method Not Allowed (for GET)
# or
# HTTP/1.1 200 OK (for POST with data)

# Send test data
curl -X POST http://YOUR_HA_IP:8123/api/torque-your-vehicle-name \
  -d "eml=test@test.com" \
  -d "k05=75" \
  -d "k0c=2000" \
  -d "k0d=50"

# Should return: {"status":"ok"} or similar
```

### Check Firewall

**On Home Assistant host**:

For Linux/Docker:
```bash
# Check if port 8123 is listening
sudo netstat -tlnp | grep 8123

# Check firewall rules
sudo iptables -L -n | grep 8123

# Allow port 8123 if blocked (example for UFW)
sudo ufw allow 8123/tcp
```

For Home Assistant OS:
- Firewall is typically disabled by default
- Check your router's firewall instead

### WiFi Troubleshooting

**AP Isolation / Client Isolation**:
- Some routers prevent devices from communicating with each other
- Check router settings for "AP Isolation" or "Client Isolation"
- Disable this feature or add an exception

**Guest Network**:
- Guest networks often isolate devices
- Connect phone to main WiFi network instead

## Debugging

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.torque_obd: debug
```

Restart Home Assistant and check logs:
1. **Settings** → **System** → **Logs**
2. Look for detailed `torque_obd` messages
3. This shows:
   - Received requests
   - Parsed data
   - Sensor updates
   - Any errors

### Check Raw Data

To see exactly what Torque is sending:

1. Enable debug logging (above)
2. Look for log entries like:
   ```
   Received data from Torque: {'eml': 'test@example.com', 'k05': '75', ...}
   ```
3. This shows the raw PID data being sent

### Test Individual PIDs

In Torque app:
1. Go to Realtime Information screen
2. Add widgets for specific PIDs
3. Observe if they update with real values
4. If a PID shows "---", your vehicle doesn't support it

### Check Integration Version

Ensure you're running the latest version:
1. Go to **HACS** (if installed via HACS)
2. Search for **Torque OBD-II**
3. Check if an update is available
4. Update if newer version exists

### Restart Everything

Sometimes a clean restart helps:
1. Close Torque app completely (force stop)
2. Restart Home Assistant
3. Wait 1 minute for full startup
4. Reopen Torque and reconnect to OBD adapter
5. Start driving

## Getting Help

If you've tried all the above and still have issues:

### Before Asking for Help

Gather this information:
1. **Home Assistant version**: Settings → System → About
2. **Integration version**: HACS → Search for Torque OBD-II
3. **Torque Pro version**: Check in Torque app settings
4. **OBD adapter model**: What adapter are you using?
5. **Vehicle details**: Year, make, model
6. **Error logs**: Copy relevant error messages from HA logs
7. **Configuration**: Your vehicle name and endpoint URL (sanitized)

### Where to Get Help

1. **GitHub Issues**: [Create an issue](https://github.com/JOHLC/Home-Assistant-Torque-OBDII/issues)
   - Best for bugs and feature requests
   - Include all information from above
   - Attach relevant logs

2. **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)
   - Search for existing topics first
   - Create new topic with detailed information
   - Tag with "custom-integration" and "torque"

3. **Home Assistant Discord**: Join the unofficial Discord
   - Real-time help from community
   - #third-party-integrations channel

### Information to Include

When asking for help, provide:

```
**Home Assistant Version**: 2023.12.1
**Integration Version**: 1.2.3
**Torque Pro Version**: 1.10.127
**OBD Adapter**: ELM327 Bluetooth v1.5
**Vehicle**: 2025 Ford Escape ST-Line

**Issue**: Sensors show unavailable

**What I've Tried**:
1. Force stopped and restarted Torque
2. Verified network connectivity
3. Checked Home Assistant logs
4. ...

**Logs**:
```
[Paste relevant log entries here]
```

**Configuration**:
- Vehicle name: 2025 Ford Escape
- Endpoint: /api/torque-2025-ford-escape
- PIDs selected in Torque: k05, k0c, k0d, k2f, kff1006
```

## Common Error Messages

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| `Connection refused` | Can't reach Home Assistant | Check network, firewall, IP address |
| `404 Not Found` | Wrong endpoint URL | Verify URL matches integration config |
| `Invalid data format` | Torque sending unexpected data | Enable debug logging to see raw data |
| `No data received` | Torque not sending anything | Check Torque logging is enabled |
| `Sensor unavailable` | No recent data for this sensor | Check if vehicle supports this PID |
| `Certificate verify failed` | SSL certificate issue | Use HTTP or install certificate |

## Security Considerations

**Remember**: Torque endpoints are **not authenticated** by design (Torque limitation).

**Security best practices**:
1. ✅ Use only on trusted local networks
2. ✅ Don't expose Home Assistant directly to internet
3. ✅ Use VPN for remote access
4. ✅ Consider firewall rules to restrict access
5. ❌ Don't port forward Home Assistant without additional security
6. ❌ Don't use on public WiFi networks

For more security information, see the [Integration README](custom_components/torque_obd/README.md#security-considerations).

---

**Still having issues?** [Open an issue on GitHub](https://github.com/JOHLC/Home-Assistant-Torque-OBDII/issues) with detailed information.

**Last Updated**: December 2025
