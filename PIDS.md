# OBD-II PID Reference Guide

This document provides a comprehensive reference of all PIDs (Parameter IDs) supported by the Torque OBD-II integration for Home Assistant.

## Table of Contents

- [What are PIDs?](#what-are-pids)
- [PID Naming Convention](#pid-naming-convention)
- [Standard OBD-II PIDs](#standard-obd-ii-pids)
- [Torque Custom PIDs](#torque-custom-pids)
- [Manufacturer-Specific PIDs](#manufacturer-specific-pids)
- [Customizing PID Definitions](#customizing-pid-definitions)

## What are PIDs?

PIDs (Parameter IDs) are standardized codes used in OBD-II (On-Board Diagnostics) to request specific data from a vehicle's ECU (Engine Control Unit). The Torque app reads these PIDs from your vehicle and sends them to Home Assistant, where they become sensor entities.

## PID Naming Convention

Torque uses a specific naming convention for PIDs:

- **Standard OBD-II PIDs**: `k` + hex value (e.g., `k05`, `k0c`, `k0d`)
  - Example: `k05` = OBD-II PID 0x05 (Engine Coolant Temperature)
  
- **Torque Custom PIDs**: `kff` + number (e.g., `kff1001`, `kff1006`)
  - These are calculated or derived values from Torque
  - GPS data, fuel economy calculations, trip data, etc.
  
- **Manufacturer-Specific PIDs**: `k` + extended hex (e.g., `k221e1c`, `k222813`)
  - Extended PIDs specific to vehicle manufacturers
  - Example: Ford transmission temperature, tire pressure sensors

## Standard OBD-II PIDs

These PIDs are defined by the OBD-II standard and should work on most vehicles manufactured after 1996.

### Engine Parameters

| PID | Hex | Name | Unit | Description |
|-----|-----|------|------|-------------|
| k03 | 0x03 | Fuel Status | - | Current fuel system status |
| k04 | 0x04 | Engine Load | % | Calculated engine load value |
| k05 | 0x05 | Engine Coolant Temperature | °C | Coolant temperature |
| k0c | 0x0C | Engine RPM | RPM | Engine revolutions per minute |
| k0e | 0x0E | Timing Advance | ° | Timing advance before TDC |
| k0f | 0x0F | Intake Air Temperature | °C | Intake manifold air temperature |
| k10 | 0x10 | Mass Air Flow Rate | g/s | Mass air flow sensor reading |
| k1f | 0x1F | Run time since engine start | s | Time since engine started |
| k42 | 0x42 | Voltage (Control Module) | V | Control module voltage |
| k43 | 0x43 | Engine Load (Absolute) | % | Absolute engine load value |
| k5c | 0x5C | Engine Oil Temperature | °C | Engine oil temperature |

### Fuel System

| PID | Hex | Name | Unit | Description |
|-----|-----|------|------|-------------|
| k06 | 0x06 | Fuel Trim Bank 1 Short Term | % | Short term fuel trim - Bank 1 |
| k07 | 0x07 | Fuel Trim Bank 1 Long Term | % | Long term fuel trim - Bank 1 |
| k08 | 0x08 | Fuel Trim Bank 2 Short Term | % | Short term fuel trim - Bank 2 |
| k09 | 0x09 | Fuel Trim Bank 2 Long Term | % | Long term fuel trim - Bank 2 |
| k0a | 0x0A | Fuel Pressure | kPa | Fuel pressure (gauge) |
| k22 | 0x22 | Fuel Rail Pressure (relative) | kPa | Fuel rail pressure relative to manifold |
| k23 | 0x23 | Fuel Rail Pressure | kPa | Fuel rail pressure (absolute) |
| k2f | 0x2F | Fuel Level | % | Fuel tank level input |
| k52 | 0x52 | Ethanol Fuel % | % | Ethanol fuel percentage |

### Throttle & Air

| PID | Hex | Name | Unit | Description |
|-----|-----|------|------|-------------|
| k11 | 0x11 | Throttle Position | % | Absolute throttle position |
| k12 | 0x12 | Air Status | - | Commanded secondary air status |
| k45 | 0x45 | Relative Throttle Position | % | Relative throttle position |
| k47 | 0x47 | Absolute Throttle Position B | % | Absolute throttle position B |
| k49 | 0x49 | Accelerator Pedal Position D | % | Accelerator pedal position D |
| k4a | 0x4A | Accelerator Pedal Position E | % | Accelerator pedal position E |
| k4b | 0x4B | Accelerator Pedal Position F | % | Accelerator pedal position F |
| k5a | 0x5A | Relative Accelerator Pedal Position | % | Relative accelerator pedal position |

### Pressure & Temperature Sensors

| PID | Hex | Name | Unit | Description |
|-----|-----|------|------|-------------|
| k0b | 0x0B | Intake Manifold Pressure | kPa | Intake manifold absolute pressure |
| k33 | 0x33 | Barometric Pressure | kPa | Barometric pressure |
| k32 | 0x32 | Evap System Vapour Pressure | kPa | Evaporative system vapor pressure |
| k46 | 0x46 | Ambient Air Temperature | °C | Ambient air temperature |

### Catalyst & Emissions

| PID | Hex | Name | Unit | Description |
|-----|-----|------|------|-------------|
| k2c | 0x2C | EGR Commanded | % | Commanded EGR |
| k2d | 0x2D | EGR Error | % | EGR error |
| k3c | 0x3C | Catalyst Temperature (Bank 1 Sensor 1) | °C | Catalyst temperature B1S1 |
| k3d | 0x3D | Catalyst Temperature (Bank 2 Sensor 1) | °C | Catalyst temperature B2S1 |
| k3e | 0x3E | Catalyst Temperature (Bank 1 Sensor 2) | °C | Catalyst temperature B1S2 |
| k3f | 0x3F | Catalyst Temperature (Bank 2 Sensor 2) | °C | Catalyst temperature B2S2 |
| k44 | 0x44 | Commanded Equivalence Ratio (lambda) | - | Commanded air-fuel equivalence ratio |
| k78 | 0x78 | Exhaust Gas Temperature 1 | °C | Exhaust gas temperature sensor 1 |
| k79 | 0x79 | Exhaust Gas Temperature 2 | °C | Exhaust gas temperature sensor 2 |

### Oxygen Sensors

| PID | Hex | Name | Unit | Description |
|-----|-----|------|------|-------------|
| k14 | 0x14 | Fuel Trim Bank 1 Sensor 1 | % | Oxygen sensor voltage B1S1 |
| k15 | 0x15 | Fuel Trim Bank 1 Sensor 2 | % | Oxygen sensor voltage B1S2 |
| k16 | 0x16 | Fuel Trim Bank 1 Sensor 3 | % | Oxygen sensor voltage B1S3 |
| k17 | 0x17 | Fuel Trim Bank 1 Sensor 4 | % | Oxygen sensor voltage B1S4 |
| k18 | 0x18 | Fuel Trim Bank 2 Sensor 1 | % | Oxygen sensor voltage B2S1 |
| k19 | 0x19 | Fuel Trim Bank 2 Sensor 2 | % | Oxygen sensor voltage B2S2 |
| k1a | 0x1A | Fuel Trim Bank 2 Sensor 3 | % | Oxygen sensor voltage B2S3 |
| k1b | 0x1B | Fuel Trim Bank 2 Sensor 4 | % | Oxygen sensor voltage B2S4 |
| k24 | 0x24 | O2 Sensor1 Equivalence Ratio | - | O2 sensor 1 equivalence ratio |
| k25 | 0x25 | O2 Sensor2 Equivalence Ratio | - | O2 sensor 2 equivalence ratio |
| k26 | 0x26 | O2 Sensor3 Equivalence Ratio | - | O2 sensor 3 equivalence ratio |
| k27 | 0x27 | O2 Sensor4 Equivalence Ratio | - | O2 sensor 4 equivalence ratio |
| k28 | 0x28 | O2 Sensor5 Equivalence Ratio | - | O2 sensor 5 equivalence ratio |
| k29 | 0x29 | O2 Sensor6 Equivalence Ratio | - | O2 sensor 6 equivalence ratio |
| k2a | 0x2A | O2 Sensor7 Equivalence Ratio | - | O2 sensor 7 equivalence ratio |
| k2b | 0x2B | O2 Sensor8 Equivalence Ratio | - | O2 sensor 8 equivalence ratio |

### Distance & Diagnostic

| PID | Hex | Name | Unit | Description |
|-----|-----|------|------|-------------|
| k21 | 0x21 | Distance travelled with MIL/CEL lit | km | Distance with malfunction indicator on |
| k31 | 0x31 | Distance travelled since codes cleared | km | Distance since diagnostic codes cleared |
| ka6 | 0xA6 | Odometer | km | Vehicle odometer reading (if available) |

## Torque Custom PIDs

These PIDs are calculated or derived by the Torque app and provide additional useful data.

### GPS & Location

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1001 | GPS Speed | km/h | Speed calculated from GPS |
| kff1005 | GPS Longitude | ° | GPS longitude coordinate |
| kff1006 | GPS Latitude | ° | GPS latitude coordinate |
| kff1007 | GPS Bearing | ° | GPS compass bearing |
| kff1010 | GPS Altitude | m | GPS altitude above sea level |
| kff1239 | GPS Accuracy | m | GPS accuracy/precision |
| kff123a | GPS Satellites | - | Number of GPS satellites |
| kff123b | GPS Bearing | ° | GPS compass bearing (alternate) |
| kff1237 | GPS vs OBD Speed difference | km/h | Difference between GPS and OBD speed |

### Fuel Economy

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1201 | Miles Per Gallon (Instant) | mpg | Instantaneous fuel economy (Imperial) |
| kff1203 | Kilometers Per Litre (Instant) | km/L | Instantaneous fuel economy (Metric) |
| kff1207 | Litres Per 100 Kilometer (Instant) | L/100km | Instantaneous fuel economy (European) |
| kff1205 | Trip average MPG | mpg | Average fuel economy for trip |
| kff1206 | Trip average KPL | km/L | Average fuel economy for trip |
| kff1208 | Trip average Litres/100 KM | L/100km | Average fuel economy for trip |
| kff5201 | Miles Per Gallon (Long Term Average) | mpg | Long term average fuel economy |
| kff5202 | Kilometers Per Litre (Long Term Average) | km/L | Long term average fuel economy |
| kff5203 | Litres Per 100 Kilometer (Long Term Average) | L/100km | Long term average fuel economy |

### Fuel Usage & Cost

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff125a | Fuel flow rate/minute | L/min | Fuel consumption rate per minute |
| kff125d | Fuel flow rate/hour | L/h | Fuel consumption rate per hour |
| kff1271 | Fuel used (trip) | L | Total fuel used during current trip |
| kff125c | Fuel cost (trip) | - | Total fuel cost for trip |
| kff126a | Distance to empty (Estimated) | km | Estimated distance until empty tank |
| kff126b | Fuel Remaining (Calculated) | % | Calculated remaining fuel percentage |
| kff126d | Cost per mile/km (Instant) | - | Instantaneous cost per distance |
| kff126e | Cost per mile/km (Trip) | - | Average cost per distance for trip |

### Trip Data

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1204 | Trip Distance | km | Distance traveled in current trip |
| kff120c | Trip distance (stored in profile) | km | Trip distance stored in vehicle profile |
| kff1266 | Trip Time (Since journey start) | s | Time since trip started |
| kff1267 | Trip time (whilst stationary) | s | Time spent stopped during trip |
| kff1268 | Trip Time (whilst moving) | s | Time spent moving during trip |
| kff1263 | Average trip speed (whilst moving) | km/h | Average speed while moving |
| kff1272 | Average trip speed (stopped or moving) | km/h | Overall average speed for trip |

### Performance Metrics

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1225 | Torque | Nm | Calculated engine torque |
| kff1226 | Horsepower (At the wheels) | hp | Calculated horsepower at wheels |
| kff1273 | Engine kW (At the wheels) | kW | Calculated power in kilowatts |
| kff1269 | Volumetric Efficiency (Calculated) | % | Calculated volumetric efficiency |

### Acceleration Times

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1277 | 0-30mph Time | s | Time to accelerate 0-30 mph |
| kff122e | 0-100kph Time | s | Time to accelerate 0-100 km/h |
| kff122d | 0-60mph Time | s | Time to accelerate 0-60 mph |
| kff124f | 0-200kph Time | s | Time to accelerate 0-200 km/h |
| kff1260 | 40-60mph Time | s | Time to accelerate 40-60 mph |
| kff125f | 60-80mph Time | s | Time to accelerate 60-80 mph |
| kff125e | 60-120mph Time | s | Time to accelerate 60-120 mph |
| kff1276 | 60-130mph Time | s | Time to accelerate 60-130 mph |
| kff1275 | 80-120kph Time | s | Time to accelerate 80-120 km/h |
| kff1261 | 80-100mph Time | s | Time to accelerate 80-100 mph |
| kff122f | 1/4 mile time | s | Quarter mile time |
| kff1230 | 1/8 mile time | s | Eighth mile time |

### Braking Times

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1264 | 100-0kph Time | s | Time to brake from 100-0 km/h |
| kff1265 | 60-0mph Time | s | Time to brake from 60-0 mph |

### Voltage & Battery

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1238 | Voltage (OBD Adapter) | V | Voltage reading from OBD adapter |

### Boost & Turbo

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1202 | Turbo Boost & Vacuum Gauge | psi | Turbo boost pressure or vacuum |

### Acceleration & Tilt Sensors

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1220 | Acceleration Sensor (X axis) | g | Acceleration in X direction |
| kff1221 | Acceleration Sensor (Y axis) | g | Acceleration in Y direction |
| kff1222 | Acceleration Sensor (Z axis) | g | Acceleration in Z direction |
| kff1223 | Acceleration Sensor (Total) | g | Total acceleration magnitude |
| kff124a | Tilt (x) | ° | Tilt angle X axis |
| kff124b | Tilt (y) | ° | Tilt angle Y axis |
| kff124c | Tilt (z) | ° | Tilt angle Z axis |

### Oxygen Sensor Voltages

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1214 | O2 Volts Bank 1 Sensor 1 | V | O2 sensor voltage B1S1 |
| kff1215 | O2 Volts Bank 1 Sensor 2 | V | O2 sensor voltage B1S2 |
| kff1216 | O2 Volts Bank 1 Sensor 3 | V | O2 sensor voltage B1S3 |
| kff1217 | O2 Volts Bank 1 Sensor 4 | V | O2 sensor voltage B1S4 |
| kff1218 | O2 Volts Bank 2 Sensor 1 | V | O2 sensor voltage B2S1 |
| kff1219 | O2 Volts Bank 2 Sensor 2 | V | O2 sensor voltage B2S2 |
| kff121a | O2 Volts Bank 2 Sensor 3 | V | O2 sensor voltage B2S3 |
| kff121b | O2 Volts Bank 2 Sensor 4 | V | O2 sensor voltage B2S4 |
| kff1240 | O2 Sensor1 wide-range Voltage | V | O2 wide-range sensor 1 voltage |
| kff1241 | O2 Sensor2 wide-range Voltage | V | O2 wide-range sensor 2 voltage |
| kff1242 | O2 Sensor3 wide-range Voltage | V | O2 wide-range sensor 3 voltage |
| kff1243 | O2 Sensor4 wide-range Voltage | V | O2 wide-range sensor 4 voltage |
| kff1244 | O2 Sensor5 wide-range Voltage | V | O2 wide-range sensor 5 voltage |
| kff1245 | O2 Sensor6 wide-range Voltage | V | O2 wide-range sensor 6 voltage |
| kff1246 | O2 Sensor7 wide-range Voltage | V | O2 wide-range sensor 7 voltage |
| kff1247 | O2 Sensor8 wide-range Voltage | V | O2 wide-range sensor 8 voltage |

### Air-Fuel Ratio

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1249 | Air Fuel Ratio (Measured) | - | Measured air-fuel ratio |
| kff124d | Air Fuel Ratio (Commanded) | - | Commanded air-fuel ratio |

### Emissions

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1257 | CO₂ in g/km (Instantaneous) | g/km | Instantaneous CO2 emissions |
| kff1258 | CO₂ in g/km (Average) | g/km | Average CO2 emissions |

### Barometric Pressure

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kff1270 | Barometer (on Android device) | kPa | Barometric pressure from phone |

## Manufacturer-Specific PIDs

### Ford Extended PIDs

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| k221e1c | Ford Transmission Temperature | °F | Transmission temperature (Ford) |
| k2203ca | Ford IAT2 (Method 2) | °C | Intake air temperature method 2 |
| k222813 | Ford Front Driver Side Tire Pressure | psi | Left front tire pressure |
| k222814 | Ford Front Passenger Side Tire Pressure | psi | Right front tire pressure |
| k222815 | Ford Rear Driver Side Tire Pressure | psi | Left rear tire pressure |
| k222816 | Ford Rear Passenger Side Tire Pressure | psi | Right rear tire pressure |

### Other Manufacturer PIDs

| PID | Name | Unit | Description |
|-----|------|------|-------------|
| kfe1805 | Transmission Temperature (Method 1) | °C | Transmission temperature (generic) |
| kb4 | Transmission Temperature (Method 2) | °C | Transmission temperature (alternate) |

## Customizing PID Definitions

You can customize any PID definition or add support for custom PIDs by creating a `torque_sensor_definitions.yaml` file in your Home Assistant configuration directory.

### Example Custom Configuration

```yaml
# Override default sensor names
k05:
  name: "My Engine Temperature"
  unit: "°C"
  icon: "mdi:thermometer"
  device_class: "temperature"
  state_class: "measurement"

# Add a completely new custom PID
kff9999:
  name: "Custom Boost Gauge"
  unit: "psi"
  icon: "mdi:gauge"
  device_class: "pressure"
  state_class: "measurement"
```

For more information on customizing sensor definitions, see the [integration README](custom_components/torque_obd/README.md#custom-sensor-definitions-optional).

## Important Notes

### Units of Measurement

**All values from Torque are sent in METRIC units**, regardless of what's displayed in the app:

- **Temperature**: Always Celsius (°C)
- **Speed**: Always kilometers per hour (km/h)
- **Distance**: Always kilometers (km)
- **Volume**: Always liters (L)
- **Pressure**: Always kilopascals (kPa)

Home Assistant will automatically convert these values based on your configured unit system preferences.

### Vehicle Compatibility

Not all vehicles support all PIDs. The availability of specific PIDs depends on:

1. **Vehicle age**: Newer vehicles typically support more PIDs
2. **Vehicle manufacturer**: Some manufacturers provide extended PIDs
3. **OBD-II adapter**: Must support the protocols used by your vehicle
4. **Torque app configuration**: PIDs must be selected in Torque for logging

### Dynamic Sensor Creation

Sensors are created **automatically** when data for a PID is received. You don't need to configure sensors manually. If a PID is not available on your vehicle, no sensor will be created for it.

### Sensor Naming

When Torque sends data, it can include custom names for each PID (via `userFullName` and `userShortName` fields). The integration prioritizes these names:

1. **First priority**: Name from Torque payload (`userFullName{PID}`)
2. **Second priority**: Name from sensor definitions (const.py or custom YAML)
3. **Third priority**: Generic name ("PID {key}")

This means your sensors will automatically use the names you've configured in the Torque app!

## Resources

- [OBD-II PIDs Wikipedia](https://en.wikipedia.org/wiki/OBD-II_PIDs) - Official OBD-II PID specifications
- [Torque Pro Documentation](https://torque-bhp.com/wiki/Main_Page) - Torque app documentation
- [Integration README](custom_components/torque_obd/README.md) - Setup and configuration guide
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions

## Contributing

Found a PID that's not listed? Want to add manufacturer-specific PIDs? Contributions are welcome! Please submit a pull request with:

1. PID code and hex value
2. Descriptive name
3. Unit of measurement
4. Description of what it measures
5. Which vehicles/manufacturers support it

---

**Last Updated**: December 2025  
**Total PIDs Documented**: 151+
