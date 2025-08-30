"""Update entity for Config Updater integration."""
import logging
import os
import subprocess
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_REPOSITORY,
    CONF_GITHUB_TOKEN,
    CONF_CONFIG_PATH,
    CONF_BRANCH,
)

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Config Updater update entity."""
    config = config_entry.data
    
    update_entity = ConfigUpdateEntity(
        hass=hass,
        config_entry=config_entry,
        repository=config[CONF_REPOSITORY],
        github_token=config.get(CONF_GITHUB_TOKEN),
        config_path=config.get(CONF_CONFIG_PATH, "/config"),
        branch=config.get(CONF_BRANCH, "main"),
    )
    
    async_add_entities([update_entity])
    
    # Set up GitHub event listener
    async def handle_github_push(event):
        """Handle GitHub push events."""
        event_data = event.data
        
        # Check if this is for our repository and main branch
        if (event_data.get("repository") == config[CONF_REPOSITORY] and 
            event_data.get("ref") == f"refs/heads/{config.get(CONF_BRANCH, 'main')}"):
            
            _LOGGER.info(f"GitHub push detected for {config[CONF_REPOSITORY]} on {config.get(CONF_BRANCH, 'main')}")
            
            # Update the entity with the latest commit info
            if "head_commit" in event_data:
                commit = event_data["head_commit"]
                update_entity.update_from_github_event(commit)
    
    # Register GitHub event listener
    hass.bus.async_listen("github_push", handle_github_push)


class ConfigUpdateEntity(UpdateEntity):
    """Config Updater update entity."""
    
    _attr_supported_features = (
        UpdateEntityFeature.INSTALL | 
        UpdateEntityFeature.RELEASE_NOTES
    )
    
    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        repository: str,
        github_token: str | None,
        config_path: str,
        branch: str,
    ) -> None:
        """Initialize the update entity."""
        self.hass = hass
        self.config_entry = config_entry
        self._repository = repository
        self._github_token = github_token
        self._config_path = config_path
        self._branch = branch
        
        self._attr_name = f"Configuration Update ({repository})"
        self._attr_unique_id = f"config_update_{repository.replace('/', '_')}"
        self._attr_title = f"Home Assistant Configuration"
        
        self._current_version = None
        self._latest_version = None
        self._latest_commit = None
        self._release_notes = None
        self._release_url = None
        
        # Start periodic check
        async_track_time_interval(hass, self._async_check_for_updates, UPDATE_INTERVAL)
        
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        # Initial check
        await self._async_check_for_updates(None)
        
    @property
    def installed_version(self) -> str | None:
        """Version currently installed."""
        return self._current_version
        
    @property
    def latest_version(self) -> str | None:
        """Latest version available."""
        return self._latest_version
        
    @property
    def release_notes(self) -> str | None:
        """Release notes of latest version."""
        return self._release_notes
        
    @property
    def release_url(self) -> str | None:
        """URL to release notes."""
        return self._release_url
        
    async def _async_check_for_updates(self, now=None) -> None:
        """Check for updates."""
        try:
            # Get current git commit
            current_commit = await self._get_current_commit()
            
            # Get latest commit from GitHub
            latest_commit_info = await self._get_latest_commit_from_github()
            
            if latest_commit_info:
                latest_commit = latest_commit_info["sha"]
                
                self._current_version = current_commit[:7] if current_commit else "unknown"
                self._latest_version = latest_commit[:7] if latest_commit else "unknown"
                
                if current_commit != latest_commit:
                    # There's an update available
                    self._latest_commit = latest_commit_info
                    self._release_notes = self._format_release_notes(latest_commit_info)
                    self._release_url = latest_commit_info.get("html_url")
                    
                self.async_write_ha_state()
                
        except Exception as e:
            _LOGGER.error(f"Error checking for updates: {e}")
            
    async def _get_current_commit(self) -> str | None:
        """Get current git commit SHA."""
        try:
            result = await self.hass.async_add_executor_job(
                subprocess.run,
                ["git", "-C", self._config_path, "rev-parse", "HEAD"],
                subprocess.PIPE,
                subprocess.PIPE,
                True  # text=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
                
        except Exception as e:
            _LOGGER.error(f"Error getting current commit: {e}")
            
        return None
        
    async def _get_latest_commit_from_github(self) -> dict[str, Any] | None:
        """Get latest commit from GitHub API."""
        try:
            url = f"https://api.github.com/repos/{self._repository}/commits/{self._branch}"
            headers = {}
            
            if self._github_token:
                headers["Authorization"] = f"token {self._github_token}"
                
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        _LOGGER.warning(f"GitHub API returned status {response.status}")
                        
        except Exception as e:
            _LOGGER.error(f"Error fetching from GitHub API: {e}")
            
        return None
        
    def _format_release_notes(self, commit_info: dict[str, Any]) -> str:
        """Format commit info as release notes."""
        commit = commit_info.get("commit", {})
        message = commit.get("message", "")
        author = commit.get("author", {}).get("name", "Unknown")
        date = commit.get("author", {}).get("date", "")
        
        # Parse date
        if date:
            try:
                parsed_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
                formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M UTC")
            except:
                formatted_date = date
        else:
            formatted_date = "Unknown"
            
        # Format message
        lines = message.split("\n")
        title = lines[0] if lines else "Configuration Update"
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        
        release_notes = f"## {title}\n\n"
        
        if body:
            release_notes += f"{body}\n\n"
            
        release_notes += f"**Author:** {author}  \n"
        release_notes += f"**Date:** {formatted_date}  \n"
        release_notes += f"**Commit:** {commit_info.get('sha', '')[:7]}\n"
        
        return release_notes
        
    @callback
    def update_from_github_event(self, commit_info: dict[str, Any]) -> None:
        """Update entity from GitHub push event."""
        self._latest_commit = commit_info
        self._latest_version = commit_info.get("id", "")[:7]
        self._release_notes = self._format_github_event_notes(commit_info)
        self._release_url = f"https://github.com/{self._repository}/commit/{commit_info.get('id', '')}"
        
        self.async_write_ha_state()
        
    def _format_github_event_notes(self, commit_info: dict[str, Any]) -> str:
        """Format GitHub event commit info as release notes."""
        message = commit_info.get("message", "")
        author = commit_info.get("author", {}).get("name", "Unknown")
        timestamp = commit_info.get("timestamp", "")
        
        # Parse timestamp
        if timestamp:
            try:
                parsed_date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M UTC")
            except:
                formatted_date = timestamp
        else:
            formatted_date = "Unknown"
            
        # Format message
        lines = message.split("\n")
        title = lines[0] if lines else "Configuration Update"
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        
        release_notes = f"## {title}\n\n"
        
        if body:
            release_notes += f"{body}\n\n"
            
        release_notes += f"**Author:** {author}  \n"
        release_notes += f"**Date:** {formatted_date}  \n"
        release_notes += f"**Commit:** {commit_info.get('id', '')[:7]}\n"
        
        return release_notes
        
    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install the update."""
        _LOGGER.info(f"Installing configuration update for {self._repository}")
        
        try:
            # Execute git pull
            result = await self.hass.async_add_executor_job(
                subprocess.run,
                ["git", "-C", self._config_path, "pull", "origin", self._branch],
                subprocess.PIPE,
                subprocess.PIPE,
                True  # text=True
            )
            
            if result.returncode != 0:
                raise HomeAssistantError(f"Git pull failed: {result.stderr}")
                
            _LOGGER.info("Successfully pulled configuration updates")
            
            # Reload relevant services
            reload_services = [
                ("automation", "reload"),
                ("script", "reload"), 
                ("scene", "reload"),
            ]
            
            for domain, service in reload_services:
                try:
                    await self.hass.services.async_call(domain, service)
                    _LOGGER.info(f"Reloaded {domain}")
                except Exception as e:
                    _LOGGER.warning(f"Failed to reload {domain}: {e}")
                    
            # Update current version
            await self._async_check_for_updates()
            
            # Create notification
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Configuration Updated",
                    "message": f"Successfully updated Home Assistant configuration from {self._repository}",
                    "notification_id": "config_update_success"
                }
            )
            
        except Exception as e:
            _LOGGER.error(f"Failed to install update: {e}")
            raise HomeAssistantError(f"Installation failed: {e}")