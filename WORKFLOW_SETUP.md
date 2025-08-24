# Home Assistant Config Check Workflow Setup

This guide explains how to set up automated Home Assistant configuration validation for your repository.

## Overview

The provided workflow will:
1. Validate Home Assistant configuration files using the official `frenck/action-home-assistant` action
2. Validate ESPHome device configurations using the ESPHome CLI
3. Run on every push to main and on all pull requests

## Installation Steps

### 1. Move the workflow file
Move the `home-assistant-config-check.yml` file to the `.github/workflows/` directory:

```bash
mkdir -p .github/workflows
mv home-assistant-config-check.yml .github/workflows/
```

### 2. Create secrets.yaml file
Create a `secrets.yaml` file in the root directory for Home Assistant validation:

```bash
# Copy the example file and customize it
cp secrets.yaml.example secrets.yaml
# Edit secrets.yaml with your actual values or placeholder values for validation
```

**Important**: Make sure to add `secrets.yaml` to your `.gitignore` file to prevent committing sensitive information:

```bash
echo "secrets.yaml" >> .gitignore
```

### 3. ESPHome secrets (if needed)
If your ESPHome configurations reference secrets not covered by the temporary secrets created in the workflow, you may need to update the ESPHome validation step in the workflow to include additional secret values.

## What gets validated

### Home Assistant Configuration
- `configuration.yaml` and all included files
- `automations.yaml`, `scripts.yaml`, `scenes.yaml`
- Custom component configurations
- Blueprint configurations
- Theme files

### ESPHome Configuration
- All `.yaml` files in the `esphome/` directory
- Syntax validation and component compatibility
- Secret reference validation (using temporary test values)

## Workflow Features

- **Parallel execution**: Home Assistant and ESPHome validations run simultaneously for faster feedback
- **Pull request integration**: Automatically validates configuration changes in PRs
- **Main branch protection**: Ensures only valid configurations are merged
- **Detailed error reporting**: Shows exactly what configuration issues need to be fixed

## Troubleshooting

### Common Issues

1. **Missing secrets**: If validation fails due to missing secrets, add them to `secrets.yaml` or update the ESPHome validation step with appropriate test values.

2. **Custom component errors**: If you have custom components that aren't available during CI validation, you may need to:
   - Add them to a `custom_components/` directory in your repo
   - Or modify the workflow to install them during validation

3. **ESPHome validation errors**: Check that all secret references in your ESPHome configs are covered by the temporary secrets created in the workflow.

## Customization

### Home Assistant Version
To use a specific Home Assistant version for validation, update the workflow:

```yaml
- name: Home Assistant Check
  uses: frenck/action-home-assistant@v1
  with:
    path: "."
    secrets: secrets.yaml
    version: "2024.1.0"  # Specify version here
```

### Additional ESPHome Secrets
To add more ESPHome secrets for validation, update the validation step:

```yaml
echo "your_secret_name: \"test_value\"" >> secrets.yaml
```

## Security Notes

- The workflow creates temporary secrets only for validation purposes
- Real secret values are never exposed in CI logs
- Make sure your actual `secrets.yaml` file is in `.gitignore`
- ESPHome secrets are created dynamically and cleaned up after validation