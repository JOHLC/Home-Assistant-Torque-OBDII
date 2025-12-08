---
applyTo: "**/tests/**/*.py"
---

Test guidelines for this repository

**Note**: This repository does not currently have automated tests. The tests/ directory contains only example payload data.

When adding tests in the future:

1. Use pytest with Home Assistant's test utilities
2. Tests must be isolated:
   - Do not make network calls or access real OBD hardware
   - Use pytest fixtures and mocks for the Torque app HTTP requests
   - Mock Home Assistant core functions and state
3. Naming:
   - Test files: test_*.py
   - Test functions: test_<functionality>
4. Coverage:
   - Test sensor creation from Torque data
   - Test PID mapping and unit conversion
   - Test config flow validation
   - Test error handling for invalid/missing data
5. Assertions:
   - Keep assertions specific and minimal
   - Verify sensor states and attributes
6. Fixtures:
   - Put reusable fixtures in tests/conftest.py
   - Create fixtures for mock Torque POST data (use tests/example-payload-data.md as reference)
   - Create fixtures for Home Assistant test environment
7. Fast and deterministic:
   - Avoid sleeps/time-dependent flakiness
   - Use Home Assistant's async test utilities
8. Running tests:
   - Use pytest -q or pytest --maxfail=1
   - Follow Home Assistant testing patterns from .github/home-assistant-developer-docs/
9. Mocking Torque data:
   - Provide reusable fixtures to simulate Torque HTTP POST requests
   - Use example data from tests/example-payload-data.md
   - Test with various PID combinations
