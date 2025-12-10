---
This repository: Home-Assistant-Torque-OBDII
Primary language: Python

Overview
This repository provides a Home Assistant custom integration for receiving vehicle data from the Torque Pro Android application via OBD-II. This is a HACS-compatible custom component with no external Python dependencies.
Whenever there are changes or anything different,  make sure to update the instructions file at: /.github/copilot-instructions.md with anything relevant. 

Repository Structure
- custom_components/torque_obd/ - Main integration code
  - __init__.py - Component initialization and setup
  - config_flow.py - UI-based configuration flow
  - sensor.py - Sensor platform implementation
  - const.py - Constants and PID mappings (151+ PIDs defined)
  - manifest.json - Integration metadata
  - README.md - Detailed setup and configuration guide
  - ARCHITECTURE.md - Technical architecture documentation
- tests/ - Example payload data (no automated tests currently)
- examples/ - Example configurations
- PIDS.md - Comprehensive PID reference guide (151+ PIDs documented)
- TROUBLESHOOTING.md - Complete troubleshooting guide
- README.md - Main project readme with quick start
- CHANGELOG.md - Version history and changes
- .github/home-assistant-developer-docs/ - Home Assistant development documentation reference
  
- Comprehensive Home Assistant developer documentation is located at: /.github/home-assistant-developer-docs/
- A few example integrations/scaffolds are located at /.github/example-custom-components/

Development Environment Setup
This is a Home Assistant custom component. For development:

1. Set up Home Assistant development environment (optional for testing):
   - Install Home Assistant Core: pip install homeassistant
   - Or use a Home Assistant development container
   
2. For code validation:
   - Install Home Assistant's hassfest validator: pip install homeassistant[validation]
   - Run validation: python -m homeassistant.scripts.hassfest validate --integration-path custom_components/torque_obd

3. For linting (if needed):
   - Install tools: pip install black flake8 pylint
   - Format code: black custom_components/
   - Lint: flake8 custom_components/ or pylint custom_components/

Code Standards & Expectations
- Follow Home Assistant development standards and conventions
- Use Home Assistant's coding style (based on PEP8)
- Use type annotations for all function signatures
- Follow Home Assistant's entity naming conventions
- Entity IDs should be prefixed with vehicle name
- All sensor values from Torque are in metric units (°C, km/h, km, L, kPa)
- Keep functions small and testable
- Handle missing or invalid data gracefully
- Log appropriately using Home Assistant's logging facilities

Integration-Specific Guidelines
- The integration domain is `torque_obd` (not just `torque`)
- Each vehicle configuration creates a unique API endpoint: `/api/torque-{vehicle_name}`
- Data is received via HTTP POST from the Torque app
- Sensors are created dynamically based on received data
- Use the PID mappings in const.py for sensor identification
- Follow Home Assistant's async conventions (use async/await)
- Use HomeAssistant's aiohttp session for HTTP requests

Important User Setup Notes
- After configuring both Home Assistant and Torque for the first time, users MUST force stop the Torque app and reopen it
- This is documented in README.md, custom_components/torque_obd/README.md, and TROUBLESHOOTING.md
- This is the most common cause of "no data appearing" issues

Acceptance Criteria for PRs
- Code follows Home Assistant conventions
- manifest.json is valid and up-to-date
- No breaking changes to existing functionality
- Clear PR title and description
- Include example configuration if adding new features
- Validate with hassfest if modifying integration structure
- Test manually with Torque app if modifying data handling
- Update documentation if changing user-facing behavior

Notes for the Agent
- This integration has no external Python dependencies (requirements: [] in manifest.json)
- Do not add unnecessary dependencies
- The integration uses Home Assistant's built-in HTTP capabilities
- Torque sends data via HTTP POST with form-encoded data
- Email parameter is optional as Torque doesn't reliably send it
- Test changes manually with the Torque Pro Android app when possible
- Reference Home Assistant developer docs in .github/home-assistant-developer-docs/ for integration patterns
