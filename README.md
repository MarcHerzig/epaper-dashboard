# Waveshare ePaper Dashboard

A modular, extensible dashboard system for the Waveshare 10.85" ePaper display (1360×480), built with Python and designed for Raspberry Pi Zero.

![Dashboard Preview](emulator_output/preview.png)

## Features

- **Modular Widget Architecture** - Plugin-based system with auto-discovery
- **YAML Configuration** - No code changes needed for customization
- **Hot-Swappable Widgets** - Enable/disable widgets without code modifications
- **Threaded Data Fetching** - Non-blocking updates for all widgets
- **Development Emulator** - Test on your Mac/PC without hardware
- **Easy Extension** - Create custom widgets with minimal boilerplate

## Built-in Widgets

| Widget | Description | Data Source |
|--------|-------------|-------------|
| **Taycan** | Porsche Taycan EV status (battery, range, charging) | Home Assistant |
| **Weather** | Temperature, humidity, wind, forecast | Open-Meteo API |
| **Air Quality** | AQI with visual indicator | Open-Meteo AQI API |
| **Clock** | Digital clock with date | System time |
| **Home Assistant** | Generic sensor display | Home Assistant API |
| **Ubiquiti** | UniFi network statistics | UniFi Controller |

## Quick Start

### Hardware Requirements

- Raspberry Pi Zero W/WH
- Waveshare 10.85" ePaper Display (1360×480)
- MicroSD Card (8GB+)
- Power Supply

### Software Installation

```bash
# Clone repository
git clone https://github.com/MarcHerzig/epaper-dashboard.git
cd epaper-dashboard

# Install dependencies
pip3 install -r requirements.txt

# Run on Raspberry Pi
python3 main.py

# Or run emulator (for development on Mac/PC)
./run_dashboard.sh
```

### Development on Mac/PC

No hardware needed! Use the built-in emulator:

```bash
# Start dashboard with live preview
./run_dashboard.sh
```

This will:
1. Force emulator mode
2. Start the dashboard
3. Open Preview.app with auto-refresh

## Configuration

All configuration is done via `config.yaml`. No code changes required!

### Example Widget Configuration

```yaml
widgets:
  - name: porsche_taycan
    type: taycan
    enabled: true
    position: [20, 20]      # X, Y coordinates
    size: [440, 300]        # Width, Height
    update_interval: 120    # Seconds between updates
    config:
      url: "https://your-homeassistant.com"
      token: "YOUR_LONG_LIVED_TOKEN"
      battery_entity: "sensor.taycan_battery_level"
      range_entity: "sensor.taycan_range"
      charging_entity: "sensor.taycan_charging_status"
      image_entity: "image.taycan_view_from_side"
```

### Display Configuration

```yaml
display:
  width: 1360
  height: 480
  refresh_interval: 60           # Seconds between screen updates
  full_refresh_cycles: 600       # Full refresh every N partial refreshes
```

## Creating Custom Widgets

Create a new widget in 3 simple steps:

### 1. Create Widget File

Create `widgets/my_widget.py`:

```python
from .base_widget import BaseWidget, WidgetRegistry
from typing import Dict, Any, Optional

@WidgetRegistry.register('my_widget')
class MyWidget(BaseWidget):
    """Your custom widget description"""

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch data from your source"""
        return {
            'value': 42,
            'status': 'active'
        }

    def render(self, draw, fonts, icon_loader):
        """Render widget on display"""
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        draw.text((x, y), f"Value: {data['value']}",
                  font=fonts['32'], fill=0)
```

### 2. Add to Configuration

Edit `config.yaml`:

```yaml
widgets:
  - name: my_custom_widget
    type: my_widget
    enabled: true
    position: [20, 340]
    size: [420, 120]
    update_interval: 60
    config:
      # Your widget-specific config
      api_key: "YOUR_API_KEY"
```

### 3. Restart Dashboard

That's it! Your widget will be auto-discovered and loaded.

## Architecture

```
┌─────────────────────────────────────────────┐
│              main.py                        │
│         (Main Event Loop)                   │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼─────────┐
         │  WidgetManager    │
         │  (Auto-Discovery) │
         └─────────┬─────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
┌─────▼─────┐ ┌───▼────┐ ┌────▼─────┐
│  Taycan   │ │Weather │ │  Clock   │
│  Widget   │ │ Widget │ │  Widget  │
└───────────┘ └────────┘ └──────────┘
      │            │            │
   (Thread)    (Thread)    (Thread)
      │            │            │
   Home          API        System
 Assistant       Data        Time
```

## Widget Lifecycle

1. **Auto-Discovery** - `WidgetManager` scans `widgets/` directory
2. **Registration** - Widgets register via `@WidgetRegistry.register()` decorator
3. **Initialization** - Widgets loaded from `config.yaml`
4. **Thread Start** - Each widget runs `fetch_data()` in background thread
5. **Rendering** - Main loop calls `render()` method for each widget
6. **Update Cycle** - Widgets refresh based on `update_interval`

## Available Fonts

Pre-configured font sizes for consistent typography:

```python
fonts = {
    '16': ImageFont, '20': ImageFont, '24': ImageFont,
    '28': ImageFont, '32': ImageFont, '40': ImageFont,
    '48': ImageFont, '60': ImageFont, '80': ImageFont,
    'clock': ImageFont  # Special large clock font
}
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python3 test_widgets.py

# Test specific widget
python3 -c "from test_widgets import *; test_widget_rendering()"
```

## Project Structure

```
.
├── main.py                 # Main application
├── config.yaml             # Configuration file
├── emulator.py             # Display emulator
├── run_dashboard.sh        # Live preview launcher
├── requirements.txt        # Python dependencies
│
├── widgets/                # Widget modules
│   ├── base_widget.py      # Base class & registry
│   ├── widget_manager.py   # Widget lifecycle manager
│   ├── taycan_widget.py    # Porsche Taycan widget
│   ├── weather_widget.py   # Weather widget
│   ├── clock_widget.py     # Clock widget
│   └── ...                 # More widgets
│
├── lib/                    # Waveshare ePaper drivers
│   └── epd_10in85.py       # Display driver
│
├── icons/                  # Widget icons
│   └── *.bmp               # 1-bit bitmap icons
│
├── fonts/                  # TrueType fonts
│   └── *.ttf               # Font files
│
└── emulator_output/        # Emulator output
    └── preview.png         # Latest render
```

## Troubleshooting

### Display not updating on Raspberry Pi

```bash
# Check SPI is enabled
sudo raspi-config
# Interface Options → SPI → Enable

# Check display connection
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

### Widget not loading

```bash
# Check logs
tail -f *.log

# Verify widget registration
python3 -c "from widgets.widget_manager import WidgetManager; \
            wm = WidgetManager({}); wm._discover_widgets(); \
            print(WidgetRegistry._widgets)"
```

### Emulator on Mac: "No module named 'PIL'"

```bash
# Install Pillow
pip3 install pillow --only-binary :all:
```

## Performance

- **Memory Usage**: ~150MB on Raspberry Pi Zero
- **CPU Usage**: <10% idle, ~30% during refresh
- **Update Speed**: ~2-3 seconds for full screen refresh
- **Partial Refresh**: <1 second for small changes

## Roadmap

- [ ] Web-based configuration UI
- [ ] More widgets (Spotify, Calendar, News, etc.)
- [ ] Support for other ePaper displays
- [ ] OTA (Over-The-Air) updates
- [ ] Mobile app for remote configuration
- [ ] Widget marketplace

## Credits

This project was inspired by [czuryk's Waveshare-ePaper-10.85-dashboard](https://github.com/czuryk/Waveshare-ePaper-10.85-dashboard).

Complete architectural redesign with modular widget system, YAML configuration, and extensive improvements.

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-widget`)
3. Commit your changes (`git commit -m 'Add amazing widget'`)
4. Push to the branch (`git push origin feature/amazing-widget`)
5. Open a Pull Request

## Support

- **Issues**: [GitHub Issues](https://github.com/MarcHerzig/epaper-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MarcHerzig/epaper-dashboard/discussions)

---

**Built with Claude Code** - AI-assisted development powered by Anthropic's Claude

Co-Authored-By: Claude <noreply@anthropic.com>
