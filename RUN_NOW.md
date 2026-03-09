# 🚀 Run Dashboard NOW!

## You just saw it working with LIVE DATA! ✅

The weather and clock widgets fetched real data successfully:
- **Weather**: 10°C, 52% humidity, AQI 27
- **Clock**: Current time and date  
- **Display**: Perfect 1360×480 emulation

---

## Quick Start (3 Commands)

### Option 1: Dashboard Only
```bash
./run_emulator.sh
```
Then view: `open emulator_output/preview.png`

### Option 2: Dashboard + Live Web Viewer (RECOMMENDED!)
```bash
./run_with_viewer.sh
```
Then open in browser: **http://localhost:8080**

Auto-refreshes every 2 seconds - you'll see updates in real-time!

### Option 3: Manual
```bash
# Terminal 1
python3 main_v2.py

# Terminal 2  
python3 viewer.py

# Browser
open http://localhost:8080
```

---

## What Works RIGHT NOW (No Config Needed)

✅ **Weather** - Live data from Open-Meteo API  
✅ **Clock** - Current time and date  
✅ **Display Emulator** - Perfect 1360×480 simulation

## What Needs Configuration

⚠️ **Home Assistant** - Add your token to config.yaml  
⚠️ **Ubiquiti** - Add your controller credentials to config.yaml

---

## To Add Your APIs

Edit `config.yaml`:

```yaml
widgets:
  - name: home_assistant
    config:
      url: "http://YOUR_HA_IP:8123"
      token: "YOUR_LONG_LIVED_TOKEN"

  - name: ubiquiti
    config:
      controller_url: "https://YOUR_UNIFI_IP:8443"
      username: "admin"
      password: "your_password"
```

Then run again - all widgets will show live data!

---

## Files Created

- `run_emulator.sh` - Run dashboard with emulator
- `run_with_viewer.sh` - Run dashboard + web viewer
- `emulator_output/preview.png` - Latest dashboard render
- `config.yaml` - All configuration

---

Enjoy your modular ePaper dashboard! 🎉
