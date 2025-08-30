# Configuration Updater Integration

This custom Home Assistant integration makes GitHub configuration updates appear as native "Update" entities in Settings > System > Updates, just like OS and service updates.

## Features

- 🔄 **Native Update Experience**: Updates appear in Settings > System > Updates
- 📝 **Rich Commit Information**: View commit messages, author, and date as release notes
- 🖱️ **One-Click Install**: Click "Install" to pull changes and reload configurations
- ⚡ **Real-time Events**: Uses GitHub integration push events for instant notifications
- 🔗 **GitHub Integration**: Direct links to commits and repository
- 🛡️ **Safe Operations**: Only reloads affected configurations, not full restart

## How It Works

1. **Monitor**: Listens for GitHub push events on your main branch
2. **Detect**: When commits are pushed, compares local vs remote commit SHAs  
3. **Notify**: Creates Update entity in Home Assistant UI with commit details
4. **Install**: When you click Install, pulls changes and reloads relevant configs
5. **Confirm**: Shows success notification when complete

## Setup Instructions

### 1. GitHub Integration Setup

Add to your `configuration.yaml`:

```yaml
github:
  access_token: !secret github_access_token
  repositories:
    - path: ketterma/homeassistant
      name: Home Assistant Config
```

Add to your `secrets.yaml`:
```yaml
github_access_token: your_github_personal_access_token_here
```

**Creating GitHub Personal Access Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (Full control of private repositories)
4. Copy the token and add it to secrets.yaml

### 2. Install Custom Integration

1. **Restart Home Assistant** to load the custom integration
2. **Add Integration**:
   - Go to Settings > Devices & Services
   - Click "Add Integration"
   - Search for "Configuration Updater"
   - Click to add

3. **Configure Integration**:
   - **Repository**: `ketterma/homeassistant` (your repo)
   - **GitHub Token**: Leave blank (uses github integration token) or provide separate token
   - **Config Path**: `/config` (default Home Assistant config directory)
   - **Branch**: `main` (branch to monitor)

### 3. Verify Setup

After setup, you should see:
- New update entity: `update.configuration_update_ketterma_homeassistant`
- Updates appear in Settings > System > Updates
- Initial version comparison (current vs latest commit)

## Usage

### Viewing Updates

1. Go to **Settings > System > Updates**
2. Configuration updates appear alongside OS updates
3. Click on update to see:
   - Commit message as title
   - Full commit details as release notes
   - Author and timestamp
   - Direct link to GitHub commit

### Installing Updates

1. Click **"Install"** on the configuration update
2. Integration performs:
   - `git pull origin main` to fetch changes
   - Selective reloading of automations, scripts, scenes
   - Success notification when complete
3. Update disappears from list (now up to date)

## What Gets Reloaded

When you install a configuration update:

- ✅ **Automations** (`automation.reload`)
- ✅ **Scripts** (`script.reload`) 
- ✅ **Scenes** (`scene.reload`)
- ✅ **Groups** (automatically detected)
- ✅ **Templates** (automatically detected)
- ❌ **Core Config** (requires full restart)
- ❌ **Integrations** (requires restart)
- ❌ **Custom Components** (requires restart)

## Troubleshooting

### Update Not Appearing

**Check GitHub Integration:**
```yaml
# In configuration.yaml - make sure this exists
github:
  access_token: !secret github_access_token
  repositories:
    - path: ketterma/homeassistant
```

**Check Integration Setup:**
- Go to Settings > Devices & Services
- Find "Configuration Updater"
- Verify repository path matches exactly

### Git Pull Fails

**Common Issues:**
- Home Assistant doesn't have git access to repository
- Repository is not cloned at `/config` 
- Authentication issues with private repositories

**Solutions:**
- Ensure `/config` is a git repository (`git status` in HA terminal)
- Verify GitHub token has repository access
- Check Home Assistant logs for specific git errors

### Services Not Reloading

**Check Logs:**
- Go to Settings > System > Logs
- Filter for "config_updater"
- Look for service reload errors

**Manual Reload:**
```yaml
# You can manually call these services
service: automation.reload
service: script.reload  
service: scene.reload
```

## Security Considerations

### GitHub Token Security

- Store token in `secrets.yaml`, never in configuration files
- Use tokens with minimal required permissions (`repo` scope only)
- Consider creating dedicated service account for automation

### Network Security  

- GitHub webhook events come through HA's GitHub integration (secure)
- No external webhooks or exposed endpoints required
- All API calls use authenticated HTTPS

### Git Repository Access

- Integration only performs `git pull` operations (read-only)
- No ability to push changes back to repository
- Local git repository should be configured with appropriate permissions

## Advanced Configuration

### Custom Reload Actions

You can customize what happens during installation by modifying the integration code or creating additional automations that respond to successful updates.

### Multiple Repositories

To monitor multiple repositories, add multiple Configuration Updater integrations with different repository paths.

### Notification Customization

The integration creates standard persistent notifications. You can create automations that respond to the `config_updater.install_update` service calls to send custom notifications.

## API Reference

### Services

**`config_updater.check_for_update`**
- Manually check for available updates
- No parameters required

**`config_updater.install_update`**  
- Manually install available updates
- No parameters required
- Same as clicking "Install" in UI

### Events

The integration listens for these Home Assistant events:

**`github_push`**
- Triggered by GitHub integration
- Contains commit information and repository details
- Filtered for configured repository and branch

## Contributing

This integration is part of the ketterma/homeassistant repository. Issues and improvements can be submitted as GitHub issues or pull requests.

## Version History

- **v1.0.0**: Initial release with GitHub integration and Update entity support