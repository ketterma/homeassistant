"""Configuration flow for Configuration Updater integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_REPO_OWNER,
    CONF_REPO_NAME,
    CONF_ACCESS_TOKEN,
    CONF_BRANCH,
    CONF_CONFIG_PATH,
    DEFAULT_BRANCH,
    DEFAULT_CONFIG_PATH,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME, default="Home Assistant Config"): str,
    vol.Required(CONF_REPO_OWNER, default="ketterma"): str,
    vol.Required(CONF_REPO_NAME, default="homeassistant"): str,
    vol.Required(CONF_ACCESS_TOKEN): str,
    vol.Optional(CONF_BRANCH, default=DEFAULT_BRANCH): str,
    vol.Optional(CONF_CONFIG_PATH, default=DEFAULT_CONFIG_PATH): str,
})


class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Configuration Updater."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the GitHub repository access
            try:
                await self._validate_repository_access(user_input)
            except ValueError as exc:
                errors["base"] = str(exc)
            else:
                # Create a unique ID based on the repository
                unique_id = f"{user_input[CONF_REPO_OWNER]}_{user_input[CONF_REPO_NAME]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def _validate_repository_access(self, user_input: dict[str, Any]) -> None:
        """Validate repository access with the provided token."""
        # For now, we'll assume the token is valid
        # In a full implementation, you would validate GitHub API access here
        if not user_input.get(CONF_ACCESS_TOKEN):
            raise ValueError("Access token is required")
        
        # Basic validation - token should be a non-empty string
        if len(user_input[CONF_ACCESS_TOKEN].strip()) < 10:
            raise ValueError("Invalid access token format")