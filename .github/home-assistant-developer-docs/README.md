# Home Assistant Developer Documentation

This directory contains Home Assistant developer documentation and conventions for this integration.

## Torque Payload Structure

The Torque app sends data in multiple payloads. See `tests/example-payload-data.md` for complete examples.

### Key Payload Fields

1. **Profile Information** (Third payload):
   - `profileName`: Vehicle name (e.g., "2025 Ford Escape ST-Line")
   - `profileFuelType`, `profileWeight`, etc.

2. **Sensor Naming** (Second/Fourth payload):
   - `userFullName{PID}`: Full sensor name (e.g., "Acceleration Sensor(Total)")
   - `userShortName{PID}`: Short sensor name (e.g., "Accel")
   - `userUnit{PID}`: Unit of measurement (DO NOT USE - frequently wrong)

3. **Sensor Values** (Fifth/Sixth payload):
   - `k{PID}`: Actual sensor value (e.g., "kff1223": "0.0")

### PID Mapping Example

From the payload, PIDs map like this:
```
userFullNameff1223: "Acceleration Sensor(Total)"
userShortNameff1223: "Accel"
userUnitff1223: "g"
```
Correlates to:
```
kff1223: "0.0"
```

## Important Rules

### Unit Handling
**CRITICAL**: The units provided by Torque (`userUnit{PID}`, `defaultUnit{PID}`) are **frequently wrong**. 

**Always assume incoming sensor values are in metric units:**
- Temperature: Celsius (°C)
- Speed: Kilometers per hour (km/h)
- Distance: Kilometers (km)
- Volume: Liters (L)
- Pressure: Kilopascals (kPa)

### Entity ID Conventions

All entity IDs must be prefixed with the device name:
- Device name: "2025 Ford Escape"
- Sensor: "Fuel Level"
- Entity ID: `sensor.2025_ford_escape_fuel_level`

**Entity ID Normalization:**
1. Convert device name to lowercase
2. Replace spaces with underscores
3. Remove special characters except underscores
4. Prepend to sensor name (also normalized)

### Sensor Name Priority

When creating sensors, use names in this priority order:
1. `userFullName{PID}` from Torque payload (if available)
2. `userShortName{PID}` from Torque payload (if available)
3. Hardcoded default name from `const.py` (fallback)
4. Generic "PID {pid}" name (last resort)

### Dynamic Sensor Creation

Sensors should be created dynamically based on incoming data:
1. Wait for sensor naming payload (`userFullName{PID}`, `userShortName{PID}`)
2. Store these names when received
3. Create sensors when actual data (`k{PID}`) arrives
4. Use stored names for sensor entities

## Home Assistant Conventions

### Sensor Attributes
- Use appropriate `device_class` (temperature, speed, etc.)
- Use appropriate `state_class` (measurement, total_increasing)
- Include proper icons using MDI (Material Design Icons)

### Device Grouping
All sensors for a vehicle should be grouped under one device using `DeviceInfo`:
- Identifiers: `{DOMAIN}_{entry_id}`
- Name: Vehicle name from configuration
- Manufacturer: "Torque"
- Model: "OBD-II"

### State Management
- Use `RestoreEntity` to persist state across restarts
- Update state using `async_write_ha_state()`
- Use dispatcher pattern for data updates
