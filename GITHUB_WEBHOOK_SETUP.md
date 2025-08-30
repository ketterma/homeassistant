# GitHub Webhook Configuration for Automated Config Deployment

This guide explains how to set up event-driven Home Assistant configuration deployment using GitHub webhooks, eliminating the need for polling.

## Overview

Instead of polling GitHub every few minutes, this solution uses GitHub webhooks to instantly notify Home Assistant when configuration changes are pushed to the main branch. This provides:

- **Real-time deployment** (seconds vs minutes)
- **Zero polling overhead** (no unnecessary API calls)
- **Intelligent reloading** (only affected components are reloaded)
- **Rich deployment notifications** with commit details

## Architecture

```
GitHub Push → GitHub Webhook → Home Assistant Webhook → Automation → Config Reload
```

## Setup Instructions

### 1. Configure GitHub Repository Webhook

In your GitHub repository (`ketterma/homeassistant`):

1. Go to **Settings** → **Webhooks**
2. Click **Add webhook**
3. Configure the webhook:
   - **Payload URL**: `https://your-home-assistant-domain.com/api/webhook/homeassistant_config_webhook`
   - **Content type**: `application/json`
   - **Secret**: (optional but recommended for security)
   - **Events**: Select "Just the push event"
   - **Active**: ✅ Checked

**Important**: Replace `your-home-assistant-domain.com` with your actual Home Assistant URL. If you're using:
- **Nabu Casa**: Use your remote URL (e.g., `abcd1234.ui.nabu-casa.org`)
- **Local Network**: Ensure GitHub can reach your Home Assistant (requires port forwarding or VPN)
- **Self-hosted tunnel**: Use your tunnel URL

### 2. Home Assistant Configuration

The automation is already configured in `automations.yaml` and webhook support is enabled in `configuration.yaml`.

#### Webhook Configuration
```yaml
# configuration.yaml
webhook:
```

#### Shell Commands
```yaml
# configuration.yaml  
shell_command:
  git_pull: 'cd /config && git pull origin main'
  git_status: 'cd /config && git status --porcelain'
  check_config: 'cd /config && hass --script check_config'
```

### 3. Security Configuration

#### Network Security
Ensure your Home Assistant HTTP configuration allows webhook access:

```yaml
# configuration.yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 172.30.33.0/24    # Your existing proxy
    # Add GitHub's IP ranges if needed
```

#### Webhook Security (Optional)
For additional security, configure webhook secrets:

```yaml
# secrets.yaml
github_webhook_secret: "your-secret-key-here"
```

```yaml
# automations.yaml (modify the webhook trigger)
- trigger: webhook
  webhook_id: "homeassistant_config_webhook"
  allowed_methods: [POST]
  local_only: false
```

## How It Works

### 1. GitHub Event Detection
When you push changes to the main branch, GitHub sends a webhook payload containing:
- Commit information (SHA, message, author)
- Changed files list (modified, added, removed)
- Repository details
- Branch reference

### 2. Intelligent Processing
The automation only triggers when:
- Push is to the `main` branch
- Repository name matches `homeassistant`
- At least one configuration file was changed:
  - `configuration.yaml`
  - `automations.yaml`
  - `scripts.yaml`
  - `scenes.yaml`
  - Files in `themes/` directory

### 3. Smart Reloading
Based on which files changed, the automation:
- **automations.yaml** → Reload automations only
- **scripts.yaml** → Reload scripts only
- **scenes.yaml** → Reload scenes only
- **themes/*.yaml** → Reload themes only
- **configuration.yaml** → Validate config + reload core config

### 4. Deployment Notification
Creates a persistent notification showing:
- Commit SHA and author
- Commit message
- Which components were reloaded
- Deployment timestamp

## Webhook Payload Example

GitHub sends a payload like this when you push:

```json
{
  "ref": "refs/heads/main",
  "repository": {
    "name": "homeassistant",
    "full_name": "ketterma/homeassistant"
  },
  "head_commit": {
    "id": "abc123def456...",
    "message": "Update driveway lighting automation",
    "author": {
      "name": "Jaxon Ketterman"
    }
  },
  "commits": [
    {
      "id": "abc123def456...",
      "message": "Update driveway lighting automation",
      "modified": ["automations.yaml"],
      "added": [],
      "removed": []
    }
  ]
}
```

## Testing the Setup

### 1. Test Webhook Delivery
1. Make a small change to a config file (e.g., add a comment)
2. Commit and push to main branch
3. Check GitHub webhook delivery in repository settings
4. Verify Home Assistant received the webhook in the logs

### 2. Test Automation
1. Check Home Assistant logs for webhook received events
2. Verify the automation was triggered
3. Look for deployment notification in Home Assistant UI
4. Confirm configuration changes were applied

### 3. Troubleshooting Commands
```bash
# Check webhook delivery status in GitHub
# Go to Settings > Webhooks > Recent Deliveries

# Check Home Assistant logs
# Settings > System > Logs > Filter by "webhook"

# Test git pull manually
# Settings > Developer Tools > Services
# Service: shell_command.git_pull
```

## Advantages Over Polling

| Aspect | Webhook (Event-Driven) | Polling |
|--------|----------------------|---------|
| **Latency** | ~5 seconds | 5+ minutes |
| **Efficiency** | Zero idle overhead | Continuous API calls |
| **Rate Limits** | No impact | GitHub API limits |
| **Reliability** | Real-time notification | Delayed detection |
| **Resource Usage** | Minimal | Continuous background activity |
| **Scalability** | Unlimited repositories | Limited by poll intervals |

## Security Considerations

### Network Access
- Webhook requires Home Assistant to be accessible from internet
- Use HTTPS for webhook URL (SSL/TLS encryption)
- Consider IP whitelisting if possible

### Authentication
- Webhook secrets provide payload verification
- Use strong, unique webhook IDs (avoid predictable names)
- Monitor webhook logs for unauthorized access attempts

### Configuration Validation
- Automation includes config validation before applying changes
- Failed configs won't be applied (safety mechanism)
- Manual rollback possible via git commands if needed

## Fallback Options

If webhook delivery fails:
1. **Manual Trigger**: Use Home Assistant Developer Tools to manually run `shell_command.git_pull`
2. **Automation Toggle**: Temporarily disable webhook automation and use manual updates
3. **Alternative Webhooks**: Configure multiple webhook endpoints for redundancy

## Monitoring and Maintenance

### Regular Checks
- Monitor webhook delivery success in GitHub
- Check Home Assistant logs for webhook processing
- Verify deployments are completing successfully
- Test webhook delivery periodically

### Log Analysis
```yaml
# Add to configuration.yaml for detailed logging
logger:
  default: warning
  logs:
    homeassistant.components.webhook: debug
    homeassistant.components.automation: info
```

This event-driven approach provides instant, efficient configuration deployment with zero polling overhead!