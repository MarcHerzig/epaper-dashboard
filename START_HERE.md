# 🚀 START HERE - LIVE Dashboard Window

## Run the LIVE Dashboard in a Window (1360×480)

Just run this **ONE COMMAND**:

```bash
./run_live.sh
```

**What happens:**
1. Dashboard starts fetching live data
2. A window opens (1360×480 - exact e-Paper size)
3. Dashboard updates every 60 seconds
4. Window refreshes every 1 second to show updates
5. You see LIVE weather, clock, and all widgets!

Press **Ctrl+C** to stop everything.

---

## What You'll See in the Window

### ✅ Live Weather Data
- Current temperature from Open-Meteo API
- Humidity, pressure, wind speed/direction
- Air quality index (AQI)
- UV index
- Weather icon (sun/moon/clouds/rain/etc)

### ✅ Live Clock
- Current time (updates every 30 seconds)
- Today's date
- Day of week

### ⚠️ Home Assistant (needs config)
- Add your token to config.yaml

### ⚠️ Ubiquiti (needs config)
- Add your controller credentials to config.yaml

---

## Alternative: Manual Control

If you want to run them separately:

**Terminal 1: Dashboard**
```bash
# Disable hardware driver (Mac only)
mv lib lib_disabled

# Run dashboard
python3 main_v2.py
```

**Terminal 2: Live Viewer Window**
```bash
python3 live_viewer.py
```

---

## Features

✅ **Exact Size**: 1360×480 pixels (same as real e-Paper)
✅ **Live Updates**: Auto-refreshes every 1 second
✅ **Real Data**: Weather and clock fetch live data
✅ **Status Bar**: Shows last update time and count
✅ **No Browser**: Native window application

---

## Troubleshooting

**"No dashboard image found"**
- Dashboard isn't running
- Run: `python3 main_v2.py` first

**Window doesn't open**
- Make sure you have Python tkinter: `pip3 install tk`
- On Mac, tkinter comes with Python

**Still showing old data**
- Dashboard updates every 60 seconds
- Wait for next refresh cycle
- Check logs: `tail -f dashboard.log`

---

## Quick Commands

```bash
# BEST: Run everything together
./run_live.sh

# Or: Just viewer (if dashboard already running)
python3 live_viewer.py

# Or: Just dashboard
python3 main_v2.py

# Test without hardware driver
mv lib lib_disabled  # Mac/Linux only
python3 main_v2.py
```

---

## What's Different from Web Viewer?

| Feature | Live Window | Web Browser |
|---------|------------|-------------|
| Display | Native GUI window | Browser tab |
| Size | Exact 1360×480 | Responsive/scaled |
| Speed | 1 second refresh | 2 second refresh |
| Setup | One command | Two terminals + browser |
| Look | Exact e-Paper view | PNG preview |

---

## Customize Your Dashboard

Edit `config.yaml` to:
- Change widget positions
- Add/remove widgets
- Configure update intervals
- Set API credentials

Then restart: `./run_live.sh`

---

Enjoy your LIVE dashboard! 🎉
