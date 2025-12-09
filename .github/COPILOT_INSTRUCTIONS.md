# Copilot Instructions Configuration

This document describes the Copilot coding agent instructions configured for the Home Assistant Torque OBD-II integration repository.
Whenever there are changes or anything different,  make sure to update the instructions file at: /.github/COPILOT_INSTRUCTIONS.md with anything relevant. 

## Overview

The repository is configured with comprehensive instructions to help GitHub Copilot coding agents understand and work with this Home Assistant custom integration effectively.

## Configuration Files

### 1. `.github/copilot-instructions.md`
The main instructions file that provides:
- **Repository overview**: Description of the project as a Home Assistant custom component
- **Repository structure**: Accurate layout of the custom_components/torque_obd/ directory
- **Development environment setup**: How to set up tools for validation and linting
- **Code standards**: Home Assistant conventions, async patterns, type hints
- **Integration-specific guidelines**: Torque app details, PID handling, multi-vehicle support
- **Acceptance criteria**: What makes a good PR for this project
- **Notes for agents**: Key considerations like no external dependencies, metric units, etc.

### 2. `.github/copilot-setup-steps.yml`
Environment setup automation that:
- Creates a Python virtual environment
- Installs Home Assistant for validation (optional)
- Installs code quality tools (black, flake8, pylint)
- Verifies the integration structure

### 3. `.github/instructions/tests.instructions.md`
Pattern-specific instructions for `**/tests/**/*.py` files:
- Notes that automated tests don't currently exist
- Provides guidelines for future test development
- Emphasizes testing with Home Assistant patterns
- References example payload data in tests/ directory

### 4. `.github/instructions/integration.instructions.md`
Pattern-specific instructions for `**/custom_components/torque_obd/**/*.py` files:
- Detailed integration architecture explanation
- Key patterns (data flow, dynamic sensors, PID handling)
- Code standards (imports, type hints, async/await, logging)
- Integration-specific rules (entity naming, units, multi-vehicle support)
- Common modification scenarios
- Testing and documentation recommendations

### 5. `.github/agents/my-agent.agent.md`
Custom agent configuration:
- Specialized knowledge about the Torque OBD-II integration
- Deep understanding of PID naming conventions
- Expertise in Home Assistant patterns
- Context about Torque Pro app limitations and behavior

### 6. `Developer documentation`
- Comprehnsive Home Assistant developer documentation is located at: 
/.github/home-assistant-developer-docs/
- A few example integrations are located at /.github/example-custom-components/

## Key Features

### Accurate to Repository Structure
Unlike generic templates, these instructions accurately reflect:
- This is a Home Assistant custom component (not a standard Python package)
- No requirements.txt or setup.py (integration has no external dependencies)
- Tests directory contains examples, not automated tests yet
- Code lives in custom_components/torque_obd/

### Integration-Specific Guidance
The instructions provide context that's crucial for working with this integration:
- Integration domain is `torque_obd` (not just `torque`)
- Each vehicle gets a unique HTTP endpoint
- Torque sends data in metric units regardless of app settings
- Dynamic sensor creation based on received PIDs
- Email parameter is optional (Torque doesn't reliably send it)

### Home Assistant Best Practices
The instructions incorporate Home Assistant conventions:
- Async/await patterns
- Config flow (UI-based configuration)
- Entity naming conventions
- Dispatcher pattern for sensor updates
- Device info for multi-vehicle support
- State restoration with RestoreEntity

### Tool Integration
Setup steps ensure coding agents can:
- Format code with black
- Lint with flake8 and pylint
- Validate integration structure
- Optionally install Home Assistant for testing

## Benefits

1. **Faster Onboarding**: New agents understand the project immediately
2. **Consistent Changes**: Agents follow established patterns and conventions
3. **Quality Assurance**: Built-in guidance for testing and validation
4. **Context Preservation**: Domain knowledge captured in instructions
5. **Reduced Errors**: Clear guidelines prevent common mistakes

## Validation

The instructions have been tested by:
1. Creating a virtual environment following the setup steps
2. Installing code quality tools (black, flake8, pylint)
3. Verifying the integration structure
4. Running black and flake8 on the codebase

All tools work correctly with the instructions provided.

## Future Enhancements

Potential improvements:
1. Add automated tests following the test instructions
2. Create GitHub Actions workflows for validation
3. Add more pattern-specific instruction files (e.g., for examples/)
4. Expand custom agent with more integration patterns
5. Add pre-commit hooks for formatting and linting

## References

- [GitHub Copilot Coding Agent Documentation](https://gh.io/copilot-coding-agent-tips)
- [Home Assistant Developer Documentation](.github/home-assistant-developer-docs/)
- [Integration Architecture](custom_components/torque_obd/ARCHITECTURE.md)
- [Integration README](custom_components/torque_obd/README.md)
