"""Config flow for Config Updater integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_CONFIG_PATH,
    DEFAULT_BRANCH,
    CONF_REPOSITORY,
    CONF_GITHUB_TOKEN,
    CONF_CONFIG_PATH,
    CONF_BRANCH,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REPOSITORY, default="ketterma/homeassistant"): cv.string,
        vol.Optional(CONF_GITHUB_TOKEN): cv.string,
        vol.Optional(CONF_CONFIG_PATH, default=DEFAULT_CONFIG_PATH): cv.string,
        vol.Optional(CONF_BRANCH, default=DEFAULT_BRANCH): cv.string,
    }
)


class ConfigUpdaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Config Updater."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate repository format
            repository = user_input[CONF_REPOSITORY]
            if "/" not in repository or len(repository.split("/")) != 2:
                errors["repository"] = "invalid_repository_format"
            else:
                # Create unique ID based on repository
                await self.async_set_unique_id(repository)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Config Updates ({repository})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "repository": "ketterma/homeassistant",
            },
        )