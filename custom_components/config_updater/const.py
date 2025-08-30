"""Constants for the Configuration Updater integration."""

DOMAIN = "config_updater"

# Configuration keys
CONF_REPO_OWNER = "repo_owner"
CONF_REPO_NAME = "repo_name"
CONF_ACCESS_TOKEN = "access_token"
CONF_BRANCH = "branch"
CONF_CONFIG_PATH = "config_path"

# Default values
DEFAULT_BRANCH = "main"
DEFAULT_CONFIG_PATH = "/config"
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

# Entity attributes
ATTR_INSTALLED_VERSION = "installed_version"
ATTR_LATEST_VERSION = "latest_version"
ATTR_RELEASE_URL = "release_url"
ATTR_SKIPPED_VERSION = "skipped_version"