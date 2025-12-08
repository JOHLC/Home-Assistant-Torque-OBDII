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
- **Corrected PID Mappings** to match standard OBD-II specifications:
  - Vehicle Speed: Changed from `k5` to `kd` (OBD-II PID 0x0D)
  - Engine Coolant Temperature: Changed from `k5900` to `k5` (OBD-II PID 0x05)
  - Intake Air Temperature: Changed from `kd` to `kf` (OBD-II PID 0x0F)

### Changed
- Sensor definitions are now loaded at integration startup
- Default sensor definitions are merged with user-defined overrides
- Improved logging for sensor definition loading and merging

### Backward Compatibility
- The integration remains fully backward compatible
- Works without the custom sensor definitions file (uses defaults)
- Users can override corrected PIDs if their Torque setup uses non-standard PIDs
- All existing installations will continue to work without changes
