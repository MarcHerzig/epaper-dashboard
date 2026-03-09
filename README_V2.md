# ePaper Dashboard v2.0 - Modular Widget System

A completely refactored, modular widget-based ePaper dashboard with easy extensibility.

## What's New in v2.0

### Modular Widget Architecture
- **Plugin System**: Add new widgets by dropping files in `widgets/` directory
- **YAML Configuration**: All settings in one `config.yaml` file
- **Auto-Discovery**: Widgets automatically registered and loaded
- **Easy Integration**: Simple base class for creating new widgets

### New Integrations
- **Home Assistant**: Display sensors, device status, energy monitoring
- **Ubiquiti UniFi**: Network traffic, WAN health, client count
- **Improved Weather**: Migrated to new architecture
- **Clock Widget**: Time and date display

### Benefits Over v1.0
- ✅ No more editing 1100-line main.py
- ✅ Add widgets without touching core code
- ✅ Share widgets between users
- ✅ Cleaner separation of concerns
- ✅ Easier debugging and maintenance

---

## Installation

### 1. Install Dependencies

```bash
pip3 install -r requirements_v2.txt
```

### 2. Configure Your Dashboard

Copy and edit the configuration file:

```bash
cp config.yaml config.yaml.backup
nano config.yaml
```

### 3. Configure Integrations

#### Home Assistant

1. Create a Long-Lived Access Token:
   - In Home Assistant, go to your Profile
   - Scroll down to "Long-Lived Access Tokens"
   - Click "Create Token"
   - Copy the token

2. Update `config.yaml`:

```yaml
widgets:
  - name: home_assistant
    type: homeassistant
    enabled: true
    config:
      url: "http://homeassistant.local:8123"
      token: "YOUR_LONG_LIVED_ACCESS_TOKEN"
      entities:
        - entity_id: "sensor.living_room_temperature"
          display_name: "Living Room"
          icon: "icon_temp"
        - entity_id: "light.living_room"
          display_name: "Lights"
          icon: "icon_bulb"
```

#### Ubiquiti UniFi

1. Get your UniFi Controller credentials
2. Update `config.yaml`:

```yaml
widgets:
  - name: ubiquiti
    type: ubiquiti
    enabled: true
    config:
      controller_url: "https://192.168.1.1:8443"
      username: "admin"
      password: "your_password"
      site: "default"
      verify_ssl: false
```

#### Weather

Update your location coordinates:

```yaml
widgets:
  - name: weather
    type: weather
    enabled: true
    config:
      latitude: 44.8240855
      longitude: 20.3834273
```

---

## Running the Dashboard

### Using tmux (recommended)

```bash
tmux new -s dashboard
python3 main_v2.py
# Detach with Ctrl+B, then D
```

To reattach:
```bash
tmux attach -t dashboard
```

### Direct Run

```bash
python3 main_v2.py
```

---

## Creating Custom Widgets

### 1. Create a New Widget File

Create `widgets/mywidget_widget.py`:

```python
"""My Custom Widget"""
import requests
from typing import Dict, Any, Optional
from .base_widget import BaseWidget, WidgetRegistry


@WidgetRegistry.register('mywidget')
class MyWidget(BaseWidget):
    """
    Description of what your widget does

    Config options:
        api_key: Your API key
        refresh_interval: How often to update
    """

    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.api_key = config['config']['api_key']

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch data from your source"""
        try:
            # Your data fetching logic here
            response = requests.get(f"https://api.example.com/data?key={self.api_key}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch data: {e}")
            return None

    def render(self, draw, fonts, icon_loader):
        """Draw the widget on screen"""
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        width, height = self.size

        # Draw your widget here
        draw.text((x, y), "My Widget", font=fonts['28'], fill=0)
        draw.text((x, y + 40), f"Value: {data.get('value', 'N/A')}",
                  font=fonts['20'], fill=0)
```

### 2. Add to Configuration

Add your widget to `config.yaml`:

```yaml
widgets:
  - name: my_custom_widget
    type: mywidget
    enabled: true
    position: [20, 300]
    size: [400, 100]
    update_interval: 120
    initial_delay: 10
    config:
      api_key: "your_api_key_here"
```

### 3. Run!

That's it! Your widget will be automatically discovered and loaded.

---

## Widget Configuration Reference

### Common Widget Options

All widgets support these options:

```yaml
- name: widget_name           # Unique identifier
  type: widget_type           # Widget type (registered name)
  enabled: true               # Enable/disable widget
  position: [x, y]            # Position on screen (pixels)
  size: [width, height]       # Widget dimensions (pixels)
  update_interval: 60         # Update frequency (seconds)
  initial_delay: 0            # Delay before first fetch (seconds)
  config:                     # Widget-specific configuration
    key: value
```

### Available Widget Types

- `homeassistant` - Home Assistant integration
- `ubiquiti` - Ubiquiti UniFi network stats
- `weather` - Weather and air quality
- `clock` - Time and date display

---

## Troubleshooting

### Check Logs

```bash
tail -f dashboard.log
```

### Test Configuration

```python
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

### Debug Mode

Edit `main_v2.py` and change:

```python
logger.setLevel(logging.DEBUG)
```

### Widget Not Loading

1. Check the widget is registered: Look for `@WidgetRegistry.register('name')`
2. Check config.yaml syntax
3. Check logs for import errors
4. Verify `enabled: true`

### Home Assistant Connection Issues

- Verify token is correct and not expired
- Check Home Assistant URL is accessible
- Test manually: `curl -H "Authorization: Bearer YOUR_TOKEN" http://homeassistant.local:8123/api/`

### Ubiquiti Connection Issues

- Try with `verify_ssl: false`
- Check controller URL is correct
- Verify credentials work in UniFi web interface

---

## Migration from v1.0

The new system runs alongside the old one. Both `main.py` and `main_v2.py` can coexist.

To migrate:

1. Keep `main.py` as backup
2. Configure `config.yaml` with your desired widgets
3. Test `main_v2.py`
4. Once satisfied, optionally rename:
   ```bash
   mv main.py main_v1_backup.py
   mv main_v2.py main.py
   ```

---

## Examples

### Minimal Configuration (Clock + Weather)

```yaml
display:
  width: 1360
  height: 480
  refresh_interval: 60

widgets:
  - name: clock
    type: clock
    enabled: true
    position: [20, 20]
    size: [600, 200]
    update_interval: 30
    config:
      format: "24h"

  - name: weather
    type: weather
    enabled: true
    position: [650, 20]
    size: [690, 440]
    update_interval: 600
    config:
      latitude: 44.8240855
      longitude: 20.3834273
```

### Home Automation Dashboard

```yaml
widgets:
  - name: home_assistant
    type: homeassistant
    enabled: true
    position: [20, 20]
    size: [660, 220]
    config:
      url: "http://homeassistant.local:8123"
      token: "YOUR_TOKEN"
      entities:
        - entity_id: "sensor.living_room_temperature"
          display_name: "Living Room"
        - entity_id: "sensor.bedroom_temperature"
          display_name: "Bedroom"
        - entity_id: "sensor.total_power"
          display_name: "Power Usage"
        - entity_id: "light.all_lights"
          display_name: "Lights"

  - name: weather
    type: weather
    enabled: true
    position: [700, 20]
    size: [640, 440]
    config:
      latitude: 44.8240855
      longitude: 20.3834273

  - name: ubiquiti
    type: ubiquiti
    enabled: true
    position: [20, 260]
    size: [660, 200]
    config:
      controller_url: "https://192.168.1.1:8443"
      username: "admin"
      password: "password"
```

---

## Contributing

Want to add more widgets? Here are some ideas:

- **MQTT**: Subscribe to MQTT topics
- **Docker**: Container status monitoring
- **Pi-hole**: DNS/ad-blocking stats
- **Plex/Jellyfin**: Media server status
- **Solar**: Solar panel production
- **Calendar**: Google Calendar events
- **GitHub**: Repository stats
- **Stock prices**: Financial data
- **RSS feeds**: News headlines

Submit your widgets via pull request!

---

## License

Same as original project. See LICENSE file.

---

## Support

- Original project: https://github.com/czuryk/Waveshare-ePaper-10.85-dashboard
- Report issues with v2.0 features in your fork
