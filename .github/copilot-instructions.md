---
This repository: Home-Assistant-Torque-OBDII
Primary language: Python

Overview
This repository provides a Home Assistant integration / helper code for reading OBD-II data (Torque). Follow the steps below so the Copilot coding agent can build, test and validate changes.

Required environment & setup
1. Create a virtualenv:
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate

2. Install dependencies:
   pip install -r requirements.txt

3. Install the package (editable mode) if applicable:
   pip install -e .

4. Run tests:
   pytest -q

Formatting and linters
- Formatting: black --check .
- Linting: flake8
- Type hints: mypy (where typing is used)

Repository structure (high-level)
- src/ or package/ : Python package code (adjust if repo uses different layout)
- tests/ : pytest test suite
- docs/ : (optional) user-facing docs and examples

Code Standards & Expectations
- Follow PEP8 and idiomatic Python.
- Use type annotations for public functions where it improves clarity.
- Write clear docstrings (Google or NumPy style).
- Keep functions small and testable. Prefer dependency injection for external resources (e.g. OBD connections).
- New features must include unit tests covering the main success and failure paths.
- Changes must pass formatting (black), linting (flake8), and tests.

Acceptance criteria for PRs Copilot should produce
- All new code has unit tests.
- All tests pass: pytest -q
- Linting and formatting checks pass.
- Clear PR title and description summarizing the change + testing notes.
- If an external API/device is involved, the agent must mock it in tests (no network or hardware calls in CI).

Notes for the agent
- Do not commit secrets or credentials.
- If changes require adding new dependencies, update requirements.txt and document why.
- If a change affects Home Assistant integration specifics, include an example configuration snippet in the PR description.

If you need me to open a PR with these files added, say "Create PR" and I will prepare and open it.
