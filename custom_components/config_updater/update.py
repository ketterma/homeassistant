"""Update entity for Configuration Updater integration."""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_REPO_OWNER,
    CONF_REPO_NAME,
    CONF_ACCESS_TOKEN,
    CONF_BRANCH,
    CONF_CONFIG_PATH,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up update entities."""
    coordinator = ConfigUpdateCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()
    
    entities = [ConfigUpdateEntity(coordinator, config_entry)]
    async_add_entities(entities)


class ConfigUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from GitHub repository."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the data update coordinator."""
        self.config_entry = config_entry
        self.repo_owner = config_entry.data[CONF_REPO_OWNER]
        self.repo_name = config_entry.data[CONF_REPO_NAME]
        self.access_token = config_entry.data[CONF_ACCESS_TOKEN]
        self.branch = config_entry.data[CONF_BRANCH]
        self.config_path = config_entry.data[CONF_CONFIG_PATH]
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from GitHub API."""
        try:
            # Get current commit hash from local git repository
            current_commit = await self._get_current_commit()
            
            # Get latest commit from GitHub
            latest_commit_info = await self._get_latest_commit_from_github()
            
            return {
                "current_commit": current_commit,
                "latest_commit": latest_commit_info["sha"],
                "latest_commit_message": latest_commit_info["message"],
                "latest_commit_date": latest_commit_info["date"],
                "latest_commit_url": latest_commit_info["url"],
                "update_available": current_commit != latest_commit_info["sha"],
            }
        except Exception as exc:
            raise UpdateFailed(f"Error fetching repository data: {exc}") from exc

    async def _get_current_commit(self) -> str:
        """Get the current commit hash from local repository."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "rev-parse", "HEAD",
                cwd=self.config_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return stdout.decode().strip()
            else:
                _LOGGER.error("Failed to get current commit: %s", stderr.decode())
                return "unknown"
        except Exception as exc:
            _LOGGER.error("Error getting current commit: %s", exc)
            return "unknown"

    async def _get_latest_commit_from_github(self) -> dict[str, Any]:
        """Get the latest commit information from GitHub API."""
        import aiohttp
        
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits/{self.branch}"
        headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"GitHub API request failed: {response.status}")
                
                data = await response.json()
                
                return {
                    "sha": data["sha"],
                    "message": data["commit"]["message"].split('\n')[0],  # First line only
                    "date": data["commit"]["committer"]["date"],
                    "url": data["html_url"],
                }


class ConfigUpdateEntity(CoordinatorEntity, UpdateEntity):
    """Configuration update entity."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES

    def __init__(self, coordinator: ConfigUpdateCoordinator, config_entry: ConfigEntry) -> None:
        """Initialize the update entity."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_config_update"
        self._attr_name = f"{config_entry.data['name']} Configuration"
        self._skipped_version: str | None = None

    @property
    def installed_version(self) -> str | None:
        """Return the currently installed version."""
        if not self.coordinator.data:
            return None
        current_commit = self.coordinator.data.get("current_commit", "unknown")
        return current_commit[:8] if current_commit != "unknown" else "unknown"

    @property
    def latest_version(self) -> str | None:
        """Return the latest available version."""
        if not self.coordinator.data:
            return None
        
        if not self.coordinator.data.get("update_available", False):
            return None
        
        latest_commit = self.coordinator.data.get("latest_commit")
        if latest_commit and latest_commit != self._skipped_version:
            return latest_commit[:8]
        
        return None

    @property
    def release_summary(self) -> str | None:
        """Return a summary of the release."""
        if not self.coordinator.data or not self.coordinator.data.get("update_available", False):
            return None
        
        commit_message = self.coordinator.data.get("latest_commit_message", "Configuration update")
        commit_date = self.coordinator.data.get("latest_commit_date")
        
        if commit_date:
            try:
                date_obj = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")
                return f"{commit_message} • {formatted_date}"
            except Exception:
                pass
        
        return commit_message

    @property
    def release_url(self) -> str | None:
        """Return the URL for release information."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("latest_commit_url")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}
        if self._skipped_version:
            attrs["skipped_version"] = self._skipped_version[:8]
        return attrs

    async def async_install(self) -> None:
        """Install the configuration update."""
        if not self.coordinator.data or not self.coordinator.data.get("update_available", False):
            raise Exception("No update available to install")

        try:
            # Pull the latest changes from the repository
            proc = await asyncio.create_subprocess_exec(
                "git", "pull", "origin", self.coordinator.branch,
                cwd=self.coordinator.config_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Git pull failed"
                raise Exception(f"Failed to pull updates: {error_msg}")

            # Reload relevant Home Assistant configurations
            await self._reload_configurations()
            
            # Create success notification
            await self._create_success_notification()
            
            # Force coordinator to update
            await self.coordinator.async_request_refresh()

        except Exception as exc:
            _LOGGER.error("Failed to install configuration update: %s", exc)
            # Create error notification
            self.hass.async_create_task(
                self.hass.services.async_call(
                    "persistent_notification",
                    "create",
                    {
                        "title": "Configuration Update Failed",
                        "message": f"Failed to install configuration update: {str(exc)}",
                        "notification_id": "config_update_error",
                    },
                )
            )
            raise

    async def async_skip(self) -> None:
        """Skip this version of the update."""
        if self.coordinator.data and self.coordinator.data.get("update_available", False):
            self._skipped_version = self.coordinator.data.get("latest_commit")
            await self.async_update_ha_state()

    async def async_release_notes(self) -> str | None:
        """Return the release notes."""
        if not self.coordinator.data or not self.coordinator.data.get("update_available", False):
            return None
        
        commit_message = self.coordinator.data.get("latest_commit_message", "")
        commit_url = self.coordinator.data.get("latest_commit_url", "")
        latest_commit = self.coordinator.data.get("latest_commit", "")[:8]
        current_commit = self.coordinator.data.get("current_commit", "")[:8]
        
        notes = f"**Configuration Update Available**\n\n"
        notes += f"**Commit:** {latest_commit}\n"
        notes += f"**Current:** {current_commit}\n\n"
        notes += f"**Message:** {commit_message}\n\n"
        
        if commit_url:
            notes += f"[View full changes on GitHub]({commit_url})\n\n"
        
        notes += "This update will pull the latest configuration from your GitHub repository and reload the affected Home Assistant components."
        
        return notes

    async def _reload_configurations(self) -> None:
        """Reload Home Assistant configurations after update."""
        try:
            # Reload core configuration components
            reload_services = [
                ("automation", "reload"),
                ("script", "reload"),
                ("scene", "reload"),
                ("group", "reload"),
            ]
            
            for domain, service in reload_services:
                try:
                    await self.hass.services.async_call(domain, service)
                except Exception as exc:
                    _LOGGER.warning("Failed to reload %s: %s", domain, exc)
            
            # Check if configuration.yaml needs a full restart
            # For now, we'll just note this - full restart requires manual intervention
            _LOGGER.info("Configuration files reloaded successfully")
            
        except Exception as exc:
            _LOGGER.error("Error reloading configurations: %s", exc)
            raise

    async def _create_success_notification(self) -> None:
        """Create a success notification after update."""
        if not self.coordinator.data:
            return
            
        commit_message = self.coordinator.data.get("latest_commit_message", "Configuration update")
        latest_commit = self.coordinator.data.get("latest_commit", "")[:8]
        
        message = f"Configuration updated successfully to {latest_commit}"
        if commit_message:
            message += f"\n\n**Latest change:** {commit_message}"
        
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Configuration Updated",
                "message": message,
                "notification_id": "config_update_success",
            },
        )