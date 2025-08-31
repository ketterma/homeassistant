# PetKit Water Notification Setup Guide

This guide will help you set up push notifications for when water is needed for your PetKit devices.

## Prerequisites

1. **PetKit Integration**: Install the PetKit integration through HACS
   - Go to HACS → Integrations → Search for "PetKit"
   - Install the PetKit integration
   - Restart Home Assistant

2. **Mobile App**: Ensure you have the Home Assistant mobile app installed and configured

## Configuration Steps

### Step 1: Configure PetKit Integration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "PetKit" and add your devices
3. Note down the entity names for your water level sensors (they will look something like):
   - `sensor.petkit_water_fountain_water_level`
   - `sensor.petkit_feeder_water_level` 
   - `binary_sensor.petkit_water_fountain_water_low`

### Step 2: Update Automation Configuration

The automation has been added to your `automations.yaml` file, but you need to customize it:

1. **Update Entity IDs**: In the automation `petkit_water_low_notification`, uncomment and update the entity_id section with your actual PetKit sensor entities.

2. **Update Notification Service**: Replace `mobile_app_device` with your actual mobile device service name. You can find this by:
   - Go to **Developer Tools** → **Services**
   - Look for services starting with `notify.mobile_app_`
   - Use the one for your device (e.g., `notify.mobile_app_iphone`)

### Step 3: Customize Notification Settings

You can adjust these settings in the automation:

- **Water Level Threshold**: Change `below: 20` to your preferred percentage
- **Notification Hours**: Modify the time conditions (`07:00:00` to `22:00:00`)
- **Notification Cooldown**: Adjust the 1-hour cooldown period in the template condition
- **Delay Before Notification**: Change the `minutes: 5` delay to prevent spam

### Step 4: Test the Setup

1. **Check Configuration**: Go to **Developer Tools** → **Check Configuration**
2. **Restart Home Assistant**: Restart to load the new automation
3. **Test Manually**: Go to **Settings** → **Automations & Scenes** → Find your PetKit automation → **Run**

## Automation Features

### Main Notification (`petkit_water_low_notification`)

- **Triggers**: When water level drops below 20% for 5+ minutes
- **Conditions**: Only during reasonable hours (7 AM - 10 PM) and not more than once per hour
- **Actions**: Sends push notification with water level percentage and "Refilled" action button

### Acknowledgment (`petkit_water_refilled_acknowledgment`)

- **Triggers**: When you tap "Refilled" button in the notification
- **Actions**: Sends confirmation that the water has been marked as refilled

## Notification Details

The notifications include:

- **Title**: 🚰 PetKit Water Low
- **Message**: Current water level percentage
- **Action Button**: "Refilled" button for quick acknowledgment
- **Priority**: High priority for immediate attention
- **Grouping**: Tagged as "pet_care" group

## Troubleshooting

### Common Issues

1. **Automation not triggering**:
   - Verify the entity IDs are correct
   - Check if the PetKit integration is working and providing data
   - Ensure the water level sensor provides numeric values

2. **Notifications not received**:
   - Verify mobile app is configured and notifications are enabled
   - Check the notification service name is correct
   - Test with Developer Tools → Services

3. **Too many notifications**:
   - Increase the cooldown period in the template condition
   - Increase the `minutes: 5` delay parameter

### Getting Entity Names

To find your PetKit entity names:

1. Go to **Developer Tools** → **States**
2. Search for "petkit" or "water"
3. Look for sensors related to water level or low water status

## Example Configuration

Here's what your entity configuration should look like once you have the PetKit integration set up:

```yaml
triggers:
- trigger: numeric_state
  entity_id: 
    - sensor.petkit_d3_water_fountain_water_level  # Example entity name
    - sensor.petkit_feeder_water_level              # Example entity name
  below: 20
  for:
    minutes: 5
```

Replace the example entity names with your actual PetKit device entity names.