# Development Guide

How to develop and test the dashboard without Raspberry Pi hardware.

---

## Quick Start (Development on Mac/Linux/Windows)

### 1. Install Dependencies

```bash
pip3 install -r requirements_v2.txt
```

### 2. Test the Emulator

```bash
python3 emulator.py
```

This will create a test pattern image in `emulator_output/` directory.

### 3. Run Tests

```bash
python3 test_widgets.py
```

This validates your widget configuration and renders a test image.

### 4. Run Dashboard with Emulator

```bash
python3 main_v2.py
```

Since you don't have the hardware driver, it will automatically use the emulator.
Output will be saved to `emulator_output/preview.png` every refresh cycle.

### 5. View in Browser (Recommended!)

In one terminal:
```bash
python3 main_v2.py
```

In another terminal:
```bash
python3 viewer.py
```

Then open http://localhost:8080 in your browser to see live updates!

---

## Emulator Features

### Display Emulator (`emulator.py`)

The emulator mimics the Waveshare 10.85" e-Paper display:

- **Resolution**: 1360×480 pixels (same as real hardware)
- **Output**: PNG files for easy viewing
- **Modes**: Supports both full refresh and partial refresh
- **Frame History**: Saves numbered frames for debugging

**Output Files:**
- `emulator_output/current.png` - Latest display state (1-bit)
- `emulator_output/preview.png` - RGB preview (easier to view)
- `emulator_output/frame_XXXX_*.png` - Frame history

**Test the emulator:**
```bash
python3 emulator.py
```

---

## Testing Tools

### Widget Test Script (`test_widgets.py`)

Comprehensive test suite for validating widgets.

**Run all tests:**
```bash
python3 test_widgets.py
```

**Run specific test:**
```bash
# Test configuration only
python3 test_widgets.py --test config

# Test widget discovery
python3 test_widgets.py --test discovery

# Test rendering
python3 test_widgets.py --test render

# Test data fetching for a specific widget
python3 test_widgets.py --test fetch --widget weather
```

**Enable verbose logging:**
```bash
python3 test_widgets.py --verbose
```

**Test output:**
- Results printed to console
- Test renders saved to `test_output/test_render.png`

---

## Web Viewer (`viewer.py`)

Real-time dashboard viewer in your browser.

**Start the viewer:**
```bash
python3 viewer.py
```

**Custom port:**
```bash
python3 viewer.py --port 8888
```

**Features:**
- Auto-refreshes every 2 seconds
- Keyboard shortcuts:
  - `R` - Refresh now
  - `Space` - Pause/resume auto-refresh
- Responsive design
- Shows update statistics

**Recommended Development Workflow:**

Terminal 1:
```bash
python3 main_v2.py
```

Terminal 2:
```bash
python3 viewer.py
```

Browser:
```
http://localhost:8080
```

Now you can edit widgets, configuration, and see updates in real-time!

---

## Development Workflow

### 1. Initial Setup

```bash
# Clone/create project
cd Waveshare-ePaper-10.85-dashboard

# Install dependencies
pip3 install -r requirements_v2.txt

# Validate setup
python3 test_widgets.py --test config
```

### 2. Create a New Widget

```bash
# Create widget file
touch widgets/mywidget_widget.py

# Edit the widget (see WIDGET_IDEAS.md for templates)
nano widgets/mywidget_widget.py

# Add to config.yaml
nano config.yaml
```

### 3. Test the Widget

```bash
# Test widget discovery
python3 test_widgets.py --test discovery

# Test initialization
python3 test_widgets.py --test init

# Test rendering
python3 test_widgets.py --test render
```

### 4. Live Development

```bash
# Terminal 1: Run dashboard
python3 main_v2.py

# Terminal 2: Run viewer
python3 viewer.py

# Terminal 3: Watch logs
tail -f dashboard.log
```

### 5. Debug Issues

```bash
# Enable debug logging
# Edit main_v2.py: logger.setLevel(logging.DEBUG)

# Test specific widget
python3 test_widgets.py --test fetch --widget mywidget --verbose

# Check configuration
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

---

## Deploying to Raspberry Pi

Once you've tested on your development machine:

### 1. Transfer Files

```bash
# From your Mac/Linux/Windows machine
rsync -avz --exclude 'emulator_output' \
           --exclude 'test_output' \
           --exclude '*.pyc' \
           --exclude '__pycache__' \
           ~/Waveshare-ePaper-10.85-dashboard/ \
           pi@raspberrypi.local:~/dashboard/
```

### 2. Install on Pi

SSH into your Pi:
```bash
ssh pi@raspberrypi.local
cd ~/dashboard
./setup_v2.sh
```

### 3. Run on Pi

```bash
# Test first
python3 main_v2.py

# If it works, run in tmux
tmux new -s dashboard
python3 main_v2.py
# Detach with Ctrl+B, then D
```

The Pi will use the real hardware driver automatically.

---

## Troubleshooting

### "No module named 'widgets'"

Make sure you're running from the project directory:
```bash
cd Waveshare-ePaper-10.85-dashboard
python3 main_v2.py
```

### "Failed to load config.yaml"

Check YAML syntax:
```bash
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

### Widget not showing up

1. Check it's registered:
   ```bash
   python3 test_widgets.py --test discovery
   ```

2. Check it's enabled in config.yaml:
   ```yaml
   - name: mywidget
     enabled: true  # Must be true!
   ```

3. Check logs:
   ```bash
   tail -f dashboard.log
   ```

### Preview image not updating

- Check emulator_output directory exists
- Check file permissions
- Try manual refresh: `python3 emulator.py`

### Viewer shows blank/old image

- Refresh browser (Ctrl+R or Cmd+R)
- Check main_v2.py is running
- Check emulator_output/preview.png exists
- Try different browser

---

## Tips & Tricks

### 1. Fast Widget Development

Use this template for quick testing:

```python
# test_my_widget.py
from widgets.mywidget_widget import MyWidget

config = {
    'enabled': True,
    'position': [0, 0],
    'size': [400, 200],
    'update_interval': 60,
    'config': {
        'api_key': 'test'
    }
}

widget = MyWidget(config, (0, 0), (400, 200))
data = widget.fetch_data()
print("Data:", data)
```

### 2. Mock APIs for Testing

Edit widget to return fake data when testing:

```python
def fetch_data(self):
    # Return mock data if in test mode
    if os.environ.get('TEST_MODE'):
        return {'value': 42, 'status': 'ok'}

    # Real API call
    ...
```

Then:
```bash
TEST_MODE=1 python3 test_widgets.py --test fetch
```

### 3. Widget Positioning Helper

Add grid lines to see widget boundaries:

```python
# In main_v2.py, after rendering widgets
if os.environ.get('DEBUG_GRID'):
    # Draw grid
    for x in range(0, width, 100):
        draw.line((x, 0, x, height), fill=0, width=1)
    for y in range(0, height, 100):
        draw.line((0, y, width, y), fill=0, width=1)
```

```bash
DEBUG_GRID=1 python3 main_v2.py
```

### 4. Performance Testing

Time widget rendering:

```python
import time

start = time.time()
widget.render(draw, fonts, icon_loader)
elapsed = time.time() - start
print(f"Widget took {elapsed*1000:.2f}ms to render")
```

### 5. Side-by-Side Comparison

Compare old vs new renders:

```bash
# Save current as reference
cp emulator_output/preview.png reference.png

# Make changes and run
python3 main_v2.py

# Compare
open reference.png emulator_output/preview.png
```

---

## CI/CD Integration

Run tests in CI pipeline:

```yaml
# .github/workflows/test.yml
name: Test Dashboard

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install -r requirements_v2.txt

      - name: Run tests
        run: python3 test_widgets.py

      - name: Upload test renders
        uses: actions/upload-artifact@v2
        with:
          name: test-renders
          path: test_output/
```

---

## Performance Considerations

### Raspberry Pi Zero Specifics

The Pi Zero is single-core and relatively slow. Keep in mind:

1. **Widget Update Intervals**: Don't update too frequently
   - Weather: 600s (10 min) is fine
   - Home Assistant: 60s (1 min) is reasonable
   - Network stats: 30s minimum

2. **Rendering Speed**: Keep widgets simple
   - Avoid complex graphics
   - Minimize font sizes (fewer antialiasing calculations)
   - Use cached icons

3. **Memory**: Pi Zero has only 512MB RAM
   - Don't load large images
   - Clean up unused objects
   - Enable garbage collection

4. **API Calls**: Stagger initial requests
   - Use `initial_delay` in config
   - Avoid API rate limits

### Optimization

Profile widget performance:

```bash
python3 -m cProfile -o profile.stats main_v2.py
python3 -m pstats profile.stats
```

---

## Hardware Testing Checklist

Before deploying to real hardware:

- [ ] All tests pass: `python3 test_widgets.py`
- [ ] Config validated: `python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"`
- [ ] All required icons present in `icons/` directory
- [ ] All required fonts present in `fnt/` directory
- [ ] API credentials configured and valid
- [ ] Update intervals appropriate for hardware
- [ ] Emulator preview looks correct
- [ ] No errors in `dashboard.log`

---

## Getting Help

1. Check logs: `tail -f dashboard.log`
2. Run tests: `python3 test_widgets.py --verbose`
3. Validate config: `python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"`
4. Check widget data: `python3 test_widgets.py --test fetch --widget <name> --verbose`

---

Happy developing! 🚀
