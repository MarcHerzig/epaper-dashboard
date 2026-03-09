# Quick Start Guide

Get the modular dashboard running in 5 minutes!

---

## For Development (Mac/Linux/Windows)

### Step 1: Install Dependencies

```bash
cd Waveshare-ePaper-10.85-dashboard
pip3 install -r requirements_v2.txt
```

### Step 2: Configure

Edit `config.yaml` with your settings:

```bash
nano config.yaml
```

**Minimum configuration** (just clock + weather):

```yaml
display:
  width: 1360
  height: 480
  refresh_interval: 60

location:
  latitude: 44.8240855    # Change to your location
  longitude: 20.3834273

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

### Step 3: Test

```bash
python3 test_widgets.py
```

If successful, you'll see:
```
✓ PASS: Widget Discovery
✓ PASS: Configuration Validation
✓ PASS: Widget Initialization
✓ PASS: Widget Rendering
```

### Step 4: Run with Live Preview

**Terminal 1:**
```bash
python3 main_v2.py
```

**Terminal 2:**
```bash
python3 viewer.py
```

**Browser:**
```
http://localhost:8080
```

You should see your dashboard updating every 60 seconds!

---

## For Raspberry Pi Zero

### Step 1: Transfer Files

From your development machine:

```bash
rsync -avz --exclude 'emulator_output' \
           --exclude '__pycache__' \
           ~/Waveshare-ePaper-10.85-dashboard/ \
           pi@raspberrypi.local:~/dashboard/
```

### Step 2: Install on Pi

```bash
ssh pi@raspberrypi.local
cd ~/dashboard
./setup_v2.sh
```

### Step 3: Configure

Edit `config.yaml` with your credentials:

```bash
nano config.yaml
```

### Step 4: Run

```bash
# Test first
python3 main_v2.py

# Watch for a minute to ensure it's working
# Press Ctrl+C to stop

# Run in background with tmux
tmux new -s dashboard
python3 main_v2.py
# Detach with Ctrl+B, then D
```

### Step 5: Autostart (Optional)

Create systemd service:

```bash
sudo nano /etc/systemd/system/dashboard.service
```

Paste:

```ini
[Unit]
Description=ePaper Dashboard
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/dashboard
ExecStart=/usr/bin/python3 /home/pi/dashboard/main_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

Check status:

```bash
sudo systemctl status dashboard.service
```

View logs:

```bash
journalctl -u dashboard.service -f
```

---

## Adding Home Assistant

### Step 1: Get Token

1. In Home Assistant, go to your Profile
2. Scroll to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Name it "ePaper Dashboard"
5. Copy the token

### Step 2: Add to Config

```yaml
widgets:
  - name: home_assistant
    type: homeassistant
    enabled: true
    position: [20, 20]
    size: [420, 200]
    update_interval: 60
    config:
      url: "http://homeassistant.local:8123"
      token: "eyJ0eXAiOiJKV1QiLC..." # Paste your token
      entities:
        - entity_id: "sensor.living_room_temperature"
          display_name: "Living Room"
          icon: "icon_temp"
        - entity_id: "light.living_room"
          display_name: "Lights"
          icon: "icon_bulb"
```

### Step 3: Test

```bash
python3 test_widgets.py --test fetch --widget homeassistant
```

---

## Adding Ubiquiti UniFi

### Step 1: Add to Config

```yaml
widgets:
  - name: ubiquiti
    type: ubiquiti
    enabled: true
    position: [20, 240]
    size: [420, 120]
    update_interval: 30
    config:
      controller_url: "https://192.168.1.1:8443"
      username: "admin"
      password: "your_password"
      site: "default"
      verify_ssl: false
      show:
        - wan_status
        - bandwidth
        - client_count
```

### Step 2: Test

```bash
python3 test_widgets.py --test fetch --widget ubiquiti
```

---

## Common Issues

### "Widget not found"

Enable it in config.yaml:
```yaml
enabled: true  # Must be true!
```

### "Failed to fetch data"

Check credentials and network:
```bash
# Test Home Assistant
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://homeassistant.local:8123/api/

# Test Ubiquiti
ping 192.168.1.1
```

### "No module named X"

Install dependencies:
```bash
pip3 install -r requirements_v2.txt
```

### Preview not updating

Refresh browser or check:
```bash
ls -ltr emulator_output/
```

---

## Next Steps

- Read [README_V2.md](README_V2.md) for full documentation
- Check [WIDGET_IDEAS.md](WIDGET_IDEAS.md) for more widget examples
- See [DEVELOPMENT.md](DEVELOPMENT.md) for development workflow

---

## Tips

**Development Mode:**
- Always test on your Mac/Linux/Windows first
- Use `python3 viewer.py` for live preview
- Check logs: `tail -f dashboard.log`

**Production Mode (Pi):**
- Use tmux or systemd for persistence
- Monitor logs: `journalctl -u dashboard.service -f`
- Set appropriate update intervals (don't overwhelm the Pi Zero)

**Widget Layout:**
- Display is 1360×480 pixels
- Use `position: [x, y]` to place widgets
- Use `size: [width, height]` to set dimensions
- Test layouts in emulator first!

---

Enjoy your new modular dashboard! 🎉
