---
applyTo: "**/custom_components/torque_obd/**/*.py"
---

Home Assistant Torque OBD-II Integration Guidelines

This file contains specific guidelines for working with the Torque OBD-II integration code.

## Integration Architecture

The integration consists of:
- `__init__.py`: Component setup, HTTP view for receiving Torque data, dynamic sensor creation
- `config_flow.py`: UI-based configuration flow for adding vehicles
- `sensor.py`: Sensor platform with dynamic sensor entities
- `const.py`: Constants, PID mappings, unit definitions, sensor definitions loader
- `manifest.json`: Integration metadata (domain, version, requirements)

## Key Patterns

### Data Flow
1. Torque app sends HTTP POST to `/api/torque-{vehicle_name}`
2. `TorqueReceiveDataView` in `__init__.py` processes the request
3. Data is parsed and dispatched via Home Assistant's dispatcher
4. Sensors are created dynamically based on received PIDs
5. Sensor states are updated with new values

### Dynamic Sensor Creation
- Sensors are created on-demand when new PIDs are received
- Each PID becomes a separate sensor entity
- Sensor metadata (name, unit, device class) comes from const.py definitions
- Entity IDs are prefixed with vehicle name for multi-vehicle support

### PID Handling
- PIDs are mapped in `const.py` using the `SENSOR_DEFINITIONS` dictionary
- Each PID has metadata: friendly name, unit, device class, state class
- Custom PID mappings can be provided via `torque_sensor_definitions.yaml`
- Handle missing PIDs gracefully - not all vehicles support all PIDs

## Code Standards

### Import Organization
Follow Home Assistant's import order:
1. Future imports (`from __future__ import annotations`)
2. Standard library
3. Third-party libraries
4. Home Assistant core imports
5. Home Assistant component imports
6. Local imports (from .const, etc.)

### Type Hints
- Use type hints for all function parameters and return values
- Use `from __future__ import annotations` for forward references
- Common types: `HomeAssistant`, `ConfigEntry`, `dict[str, Any]`

### Async/Await
- All integration functions should be async
- Use `async def` for all entry points
- Use `await` for I/O operations
- Use `hass.async_add_executor_job()` for blocking operations

### Logging
- Use module-level logger: `_LOGGER = logging.getLogger(__name__)`
- Log levels:
  - DEBUG: Detailed information for debugging
  - INFO: Important state changes, setup completion
  - WARNING: Unexpected but handled situations
  - ERROR: Errors that prevent functionality
- Include relevant context in log messages (vehicle name, PID, etc.)

### Error Handling
- Handle invalid/missing data gracefully
- Don't crash on bad input from Torque app
- Return appropriate HTTP status codes (200, 400, 500)
- Log errors with context for debugging

## Integration-Specific Rules

### Entity Naming
- Entity IDs: `sensor.{vehicle_name}_{sensor_name}`
- Sanitize vehicle names for entity IDs (replace spaces, lowercase)
- Sensor names should be human-readable from Torque or const.py
- Use Home Assistant's entity naming conventions

### Units and Conversions
- Torque sends ALL data in metric units (°C, km/h, km, L, kPa)
- Home Assistant will convert based on user preferences
- Define units in const.py using Home Assistant's unit constants
- Use appropriate device classes for automatic unit handling

### Multi-Vehicle Support
- Each vehicle gets its own config entry
- Each vehicle has a unique API endpoint
- Data is isolated by config entry ID
- Device info should distinguish between vehicles

### State Management
- Use RestoreEntity for sensors that should persist state
- Mark diagnostic sensors with EntityCategory.DIAGNOSTIC
- Use STATE_UNAVAILABLE when vehicle not reporting
- Use STATE_UNKNOWN for uninitialized sensors

### HTTP Endpoint
- Endpoint pattern: `/api/torque-{vehicle_name_slug}`
- Accept POST requests with form-encoded data
- Validate vehicle name/email if required
- Return JSON response for Torque app

## Common Modifications

### Adding New PID Mappings
1. Add entry to `SENSOR_DEFINITIONS` in const.py
2. Include: pid, name, unit, device_class, state_class
3. Test with Torque app sending that PID
4. Update documentation

### Changing Data Processing
1. Modify `TorqueReceiveDataView._process_request` in `__init__.py`
2. Maintain backward compatibility with existing data
3. Handle edge cases (missing fields, invalid values)
4. Add logging for debugging

### Modifying Sensor Behavior
1. Update `TorqueSensor` class in sensor.py
2. Consider impact on existing sensors
3. Test state restoration after restart
4. Verify device info is correct

## Testing Recommendations

When making changes:
1. Test with actual Torque Pro app and OBD adapter
2. Test multi-vehicle scenarios
3. Test Home Assistant restart (state restoration)
4. Test invalid/missing data handling
5. Check logs for errors or warnings
6. Verify entity IDs and names are correct

## Documentation

When adding features:
- Update custom_components/torque_obd/README.md
- Update main README.md if user-facing
- Add example configuration to examples/ if needed
- Update CHANGELOG.md with changes
