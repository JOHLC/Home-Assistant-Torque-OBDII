# Changelog

## [Unreleased]

### Added
- **Custom Sensor Definitions**: Added support for user-defined sensor definitions via `torque_sensor_definitions.yaml` file
  - Place the file in your Home Assistant config directory to customize or add sensor definitions
  - Custom definitions override default definitions
  - Supports adding completely new PIDs
  - See `custom_components/torque_obd/torque_sensor_definitions.yaml.example` for examples
  
- Comprehensive documentation for custom sensor configuration in README.md
- Example sensor definitions file with detailed comments

### Fixed
- **State Persistence After Reboot**: Fixed sensor data showing as "unavailable" after Home Assistant restart
  - Sensors now correctly display their last known values after reboot
  - State restoration was working internally but not writing to Home Assistant's state machine
  - Added `async_write_ha_state()` call after state restoration to persist values across restarts
  
- **Corrected PID Mappings** to match standard OBD-II specifications with proper leading zeros:
  - Fixed single-digit hex PIDs to include leading zero (e.g., `k5` → `k05`, `kc` → `k0c`, `kd` → `k0d`, `kf` → `k0f`)
  - Corrected GPS sensor mappings to match reference table:
    - `kff1001`: GPS Latitude → **GPS Speed** (was incorrect)
    - `kff1005`: GPS Altitude → **GPS Longitude** (was incorrect)
    - `kff1006`: GPS Speed → **GPS Latitude** (was incorrect)
    - `kff1010`: GPS Bearing → **GPS Altitude** (was incorrect)
  - Added 135+ missing standard OBD-II PID definitions from the OBDII reference table
  - PIDs now correctly map to their OBD-II hex codes: `k{hex}` format
  - Notable additions: `k1f` (Run time), `k21` (MIL distance), `k31` (Distance since codes cleared), `k3c` (Catalyst temp), `k42` (Control module voltage)
  - Total PIDs defined increased from ~25 to 143

### ⚠️ Breaking Changes
- **Entity IDs will change** for sensors using corrected PID keys:
  - Sensors with old keys (e.g., `k5`, `kc`, `kd`) will be recreated with correct keys (e.g., `k05`, `k0c`, `k0d`)
  - GPS sensor names corrected to match actual data (e.g., kff1006 is now GPS Latitude, not GPS Speed)
  - Historical data for these sensors will not automatically migrate
  - **Recommendation**: Note your current sensor entity IDs before updating if you have automations or dashboards referencing them
- **Sensor Display Precision**: All numeric sensors now default to 2 decimal places (e.g., 69.41% instead of 69.4117647058823%)
  - Users can customize precision per sensor in the Home Assistant UI
  - Applies to all sensors with numeric values
- **Entity ID Prefixing**: Fixed entity IDs to properly include vehicle name prefix
  - Entities now appear as `sensor.vehicle_name_sensor_name` instead of `sensor.sensor_name`
  - Prevents conflicts when using multiple vehicles
  - Example: `sensor.2025_ford_escape_fuel_level` instead of `sensor.fuel_level`

### Changed
- Sensor definitions are now loaded at integration startup
- Default sensor definitions are merged with user-defined overrides
- Improved logging for sensor definition loading and merging
- Sensor names now include vehicle name for proper entity ID generation

### Backward Compatibility
- The integration remains fully backward compatible
- Works without the custom sensor definitions file (uses defaults)
- Users can override corrected PIDs if their Torque setup uses non-standard PIDs
- All existing installations will continue to work without changes
