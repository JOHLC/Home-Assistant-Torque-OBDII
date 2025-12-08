"""Config flow for Torque OBD-II integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import CONF_EMAIL, CONF_VEHICLE_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VEHICLE_NAME): cv.string,
        vol.Optional(CONF_EMAIL): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.
    
    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    _LOGGER.debug("Validating config flow input for vehicle '%s'", data.get(CONF_VEHICLE_NAME, "Unknown"))
    
    # Validate vehicle name
    vehicle_name = data[CONF_VEHICLE_NAME].strip()
    if not vehicle_name:
        _LOGGER.warning("Validation failed: Vehicle name is empty")
        raise ValueError("Vehicle name cannot be empty")
    
    # Validate that vehicle name is alphanumeric with spaces, dashes, or underscores only
    if not re.match(r'^[a-zA-Z0-9 _-]+$', vehicle_name):
        _LOGGER.warning("Validation failed: Vehicle name '%s' contains invalid characters", vehicle_name)
        raise ValueError("Vehicle name contains invalid characters")
    
    _LOGGER.debug("Vehicle name '%s' validated successfully", vehicle_name)
    
    # Validate email format if provided
    if CONF_EMAIL in data and data[CONF_EMAIL]:
        email = data[CONF_EMAIL]
        _LOGGER.debug("Validating email: %s", email)
        
        # Basic email validation: must have @ and . with reasonable structure
        if "@" not in email or "." not in email:
            _LOGGER.warning("Validation failed: Email '%s' has invalid format", email)
            raise ValueError("Invalid email format")
        
        # Check that @ comes before the last .
        at_pos = email.rfind("@")
        dot_pos = email.rfind(".")
        if at_pos >= dot_pos or at_pos == 0 or dot_pos == len(email) - 1:
            _LOGGER.warning("Validation failed: Email '%s' has invalid format", email)
            raise ValueError("Invalid email format")
        
        # Check there's content on both sides of @
        parts = email.split("@")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            _LOGGER.warning("Validation failed: Email '%s' has invalid format", email)
            raise ValueError("Invalid email format")
        
        _LOGGER.debug("Email '%s' validated successfully", email)
    
    _LOGGER.debug("All validation checks passed for vehicle '%s'", vehicle_name)
    
    # Return info to be stored in the config entry
    return {"title": vehicle_name}


class TorqueConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Torque OBD-II."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Starting Torque OBD-II config flow (user step)")
        errors: dict[str, str] = {}
        
        if user_input is not None:
            _LOGGER.debug("Processing user input for vehicle '%s'", user_input.get(CONF_VEHICLE_NAME, "Unknown"))
            try:
                info = await validate_input(self.hass, user_input)
            except ValueError as err:
                if "Vehicle name" in str(err):
                    _LOGGER.warning("Config flow validation error: %s", err)
                    errors["base"] = "invalid_vehicle_name"
                else:
                    _LOGGER.warning("Config flow validation error: %s", err)
                    errors["base"] = "invalid_email"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during config flow validation")
                errors["base"] = "unknown"
            else:
                # Check if already configured - use vehicle name as unique identifier
                # Normalize vehicle name for unique_id (same as URL: lowercase, spaces to dashes)
                normalized_name = user_input[CONF_VEHICLE_NAME].lower().replace(' ', '-')
                _LOGGER.debug("Setting unique_id to normalized vehicle name: %s", normalized_name)
                await self.async_set_unique_id(normalized_name)
                self._abort_if_unique_id_configured()
                
                _LOGGER.info("Creating config entry for vehicle '%s'", info["title"])
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
