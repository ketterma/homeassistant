# GitHub Configuration Updates Setup Guide

This guide will help you set up automatic Home Assistant configuration updates that appear as native "Update" entities in your Settings > System > Updates.

## Quick Setup

### 1. Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a name: `HomeAssistant Config Updates`
4. Select scope: **`repo`** (Full control of private repositories)
5. Click **"Generate token"**
6. Copy the token (save it securely - you won't see it again)

### 2. Add Token to Home Assistant

Add this to your `secrets.yaml` file:
```yaml
github_access_token: ghp_your_token_here_replace_with_actual_token
```

### 3. Restart Home Assistant

Restart Home Assistant to load the new GitHub integration and custom components.

### 4. Configure the Integration  

1. Go to **Settings > Devices & Services**
2. Click **"+ Add Integration"** 
3. Search for **"Configuration Updater"**
4. Click to add and configure:
   - **Repository**: `ketterma/homeassistant`
   - **GitHub Token**: Leave blank (uses existing token)
   - **Config Path**: `/config` 
   - **Branch**: `main`

### 5. Test the Setup

1. Go to **Settings > System > Updates**
2. You should see **"Configuration Update (ketterma/homeassistant)"**
3. If your local config is behind the GitHub main branch, you'll see an update available

## How It Works

### The Workflow
```
1. Push commits to main branch
2. GitHub integration sends push event to Home Assistant  
3. Configuration Updater creates Update entity
4. Update appears in Settings > System > Updates
5. Click Install to pull changes and reload configs
6. Success notification when complete
```

### What You'll See

**In Settings > System > Updates:**
- Configuration updates appear alongside OS updates
- Click to see commit message, author, date as "release notes"
- Direct links to GitHub commits
- One-click Install button

**When You Install:**
- Performs `git pull origin main`
- Reloads automations, scripts, scenes automatically  
- Shows success notification
- Update disappears (now up to date)

## Example Workflow

1. **Make Changes**: Edit `automations.yaml` in GitHub web interface or local editor
2. **Commit & Push**: Commit to main branch  
3. **Notification**: Home Assistant shows update available within seconds
4. **Review**: Click update to see what changed
5. **Install**: Click Install to apply changes
6. **Complete**: Automations reload automatically

## Troubleshooting

### No Updates Showing

**Check Configuration:**
- Verify `configuration.yaml` has GitHub integration configured
- Check `secrets.yaml` has valid `github_access_token`
- Ensure Configuration Updater integration is added

**Check Integration:**
- Go to Settings > Devices & Services
- Find "Configuration Updater" 
- Verify settings match your repository

### Installation Fails

**Common Issues:**
- Home Assistant can't access git repository
- Invalid or expired GitHub token
- Permission issues with config directory

**Solutions:**
- Check Home Assistant logs for specific errors
- Verify token has `repo` permissions
- Ensure `/config` is a valid git repository

## Security Notes

- GitHub token is stored securely in `secrets.yaml`
- Only `git pull` operations are performed (read-only)
- No external webhooks or exposed endpoints
- Uses Home Assistant's existing GitHub integration

## Next Steps

Once setup is complete:

1. **Test**: Make a small change and push to main
2. **Verify**: Check that update appears in HA
3. **Install**: Try installing an update
4. **Monitor**: Check logs for any issues

You now have full CI/CD for your Home Assistant configuration with manual approval! 🎉