# Configuration Updater Integration

This custom Home Assistant integration provides a user-friendly way to manage configuration updates from a GitHub repository. Instead of automatically applying changes, updates appear as "updates" in Home Assistant's Settings > System > Updates section, allowing for manual approval and installation.

## Features

- **Visual Update Management**: Configuration updates appear alongside OS and service updates in the Home Assistant UI
- **Manual Approval**: Choose when to apply configuration changes instead of automatic deployment
- **Rich Information**: View commit messages, dates, and direct links to GitHub changes
- **Selective Updates**: Skip specific updates if needed
- **Smart Reloading**: Automatically reloads relevant Home Assistant components after installation
- **Status Notifications**: Get notified of successful updates or errors

## Installation

1. **Copy Integration**: Place this `config_updater` folder in your `custom_components/` directory
2. **Restart Home Assistant**: Restart to load the new integration
3. **Add Integration**: Go to Settings > Devices & Services > Add Integration > "Configuration Updater"
4. **Configure Repository**: Provide your GitHub repository details and access token

## Configuration

When adding the integration, you'll need to provide:

- **Name**: Display name for the update entity (e.g., "Home Assistant Config")
- **Repository Owner**: Your GitHub username (e.g., "ketterma")  
- **Repository Name**: Repository name (e.g., "homeassistant")
- **Access Token**: GitHub personal access token with repo read permissions
- **Branch**: Branch to monitor for updates (default: "main")
- **Config Path**: Local path to your config directory (default: "/config")

### GitHub Access Token

Create a Personal Access Token at: https://github.com/settings/tokens

Required permissions:
- `repo` (for private repositories) or `public_repo` (for public repositories)

## How It Works

1. **Monitoring**: The integration checks your GitHub repository every 5 minutes for new commits
2. **Update Detection**: When new commits are found, an update entity appears in Settings > System > Updates
3. **Update Information**: View commit messages, timestamps, and GitHub links before applying
4. **Manual Installation**: Click "Install" to pull changes and reload configurations
5. **Automatic Reloading**: Relevant services (automations, scripts, scenes) reload automatically

## Update Process

When you install an update:

1. **Git Pull**: Latest changes are pulled from your GitHub repository
2. **Configuration Reload**: Home Assistant reloads:
   - Automations (`automation.reload`)
   - Scripts (`script.reload`)
   - Scenes (`scene.reload`)
   - Groups (`group.reload`)
3. **Notifications**: Success or error notifications are displayed
4. **Status Update**: Update entity reflects the new installed version

## Security Considerations

- **Access Token Security**: Store your GitHub token securely in Home Assistant's configuration
- **Repository Validation**: Only the configured repository and branch are monitored
- **Local Git Repository**: Requires a properly initialized git repository in your config directory
- **Manual Control**: Updates never install automatically - user approval is always required

## Troubleshooting

### No Updates Appearing
- Check that your config directory is a git repository (`git status` should work)
- Verify GitHub access token has correct permissions
- Ensure repository owner/name are correct
- Check Home Assistant logs for API errors

### Installation Failures
- Verify git repository is clean (no uncommitted changes)
- Check network connectivity to GitHub
- Ensure Home Assistant has write permissions to config directory
- Review Home Assistant logs for specific error messages

### Configuration Not Reloading
- Some changes require a full Home Assistant restart
- Check individual service logs (automation, script, etc.)
- Validate YAML syntax before pushing changes

## Integration with CI/CD

This integration pairs perfectly with GitHub Actions for configuration validation:

1. **Push Changes**: Commit and push configuration changes to GitHub
2. **CI Validation**: GitHub Actions validate configuration syntax
3. **Update Notification**: Home Assistant shows the update in the UI
4. **Manual Approval**: Review and install the update when ready
5. **Automatic Reload**: Home Assistant applies changes and reloads services

## Example Workflow

1. Edit configuration files locally or in GitHub web interface
2. Commit and push changes to your repository  
3. GitHub Actions runs validation checks
4. Home Assistant detects the update within 5 minutes
5. Navigate to Settings > System > Updates
6. Review the commit message and click "Install"
7. Configuration is updated and services are reloaded automatically

This provides full CI/CD capabilities while maintaining manual control over when changes are applied to your running Home Assistant instance.