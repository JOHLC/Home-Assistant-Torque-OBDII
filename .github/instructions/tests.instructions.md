---
applyTo: "**/tests/**/*.py"
---

Test guidelines for this repository

1. Use pytest
2. Tests must be isolated:
   - Do not make network calls or access real OBD hardware.
   - Use pytest fixtures and mocks for hardware / external APIs (e.g., mock the OBD connection object).
3. Naming:
   - Test files: test_*.py
   - Test functions: test_function_name
4. Coverage:
   - New features should include tests for success cases, error handling, and edge cases.
5. Assertions:
   - Keep assertions specific and minimal; prefer single-responsibility assertions per test.
6. Fixtures:
   - Put reusable fixtures in tests/conftest.py
7. Fast and deterministic:
   - Avoid sleeps/time-dependent flakiness. Use monkeypatch to freeze time where necessary.
8. Running tests:
   - Use pytest -q or pytest --maxfail=1
9. Mocking hardware:
   - Provide a reusable helper or fixture to simulate OBD-II responses (example in tests/fixtures_obd.py).
