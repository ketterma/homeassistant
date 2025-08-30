"""Configuration Updater integration for Home Assistant."""
import logging
import os
import subprocess
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.UPDATE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Config Updater from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_check_for_update(call: ServiceCall) -> None:
        """Handle the check for update service."""
        _LOGGER.debug("Checking for configuration updates")
        # This will be handled by the update entity

    async def handle_install_update(call: ServiceCall) -> None:
        """Handle the install update service."""
        _LOGGER.info("Installing configuration update")
        
        config_path = entry.data.get("config_path", "/config")
        
        try:
            # Execute git pull
            result = await hass.async_add_executor_job(
                subprocess.run,
                ["git", "-C", config_path, "pull", "origin", "main"],
                subprocess.PIPE,
                subprocess.PIPE,
                True  # text=True
            )
            
            if result.returncode == 0:
                _LOGGER.info("Successfully pulled configuration updates")
                
                # Reload relevant services
                reload_services = [
                    "homeassistant.reload_config_entry",
                    "automation.reload", 
                    "script.reload",
                    "scene.reload"
                ]
                
                for service in reload_services:
                    try:
                        domain, service_name = service.split(".", 1)
                        await hass.services.async_call(domain, service_name)
                    except Exception as e:
                        _LOGGER.warning(f"Failed to reload {service}: {e}")
                        
            else:
                _LOGGER.error(f"Git pull failed: {result.stderr}")
                
        except Exception as e:
            _LOGGER.error(f"Failed to install update: {e}")

    hass.services.async_register(DOMAIN, "check_for_update", handle_check_for_update)
    hass.services.async_register(DOMAIN, "install_update", handle_install_update)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok