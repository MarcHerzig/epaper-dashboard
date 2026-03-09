# How to View the Live Dashboard

## The Issue with GUI Windows

The tkinter GUI window doesn't work when running through Claude Code (remote/headless environment).

**But there's a BETTER solution for Mac!**

---

## ✅ Solution: Use Mac Preview App (Auto-Refreshes!)

Mac's Preview app **automatically refreshes** when image files change. This is perfect for viewing the dashboard live!

### Run This:

```bash
./run_dashboard.sh
```

**What happens:**
1. Dashboard starts and runs continuously
2. Preview app opens showing the dashboard (1360×480)
3. **Preview auto-refreshes** every time the dashboard updates (60 sec)
4. You see live weather, clock, and all widgets!

### In Preview App:
- **Cmd+0** = View at actual size (1:1 pixels)
- **Cmd+1** = Fit to window
- **Cmd+Plus/Minus** = Zoom in/out
- Image auto-updates when dashboard refreshes!

---

## Alternative: Manual Refresh

If you want manual control:

### Terminal 1: Run Dashboard
```bash
# Disable hardware (Mac only)
mv lib lib_disabled

# Run dashboard
python3 main_v2.py
```

### Terminal 2: View Output
```bash
# Open with Preview
open -a Preview emulator_output/preview.png

# Or with default image viewer
open emulator_output/preview.png

# Or just check the file
ls -lh emulator_output/preview.png
```

The image updates every 60 seconds. Preview will auto-reload it!

---

## Web Viewer (If You Need It)

If you prefer browser-based viewing:

### Terminal 1: Dashboard
```bash
mv lib lib_disabled
python3 main_v2.py
```

### Terminal 2: Web Server
```bash
python3 viewer.py
```

### Browser
```
http://localhost:8080
```

But honestly, **Preview app is better** on Mac because:
- ✅ Native app
- ✅ Auto-refreshes
- ✅ View at actual 1360×480 size
- ✅ No browser needed

---

## What You're Viewing

The dashboard shows:

### ✅ Live Weather (every 10 minutes)
- Temperature from Open-Meteo API
- Humidity, pressure, wind
- Air quality index (AQI)
- UV index
- Weather icons

### ✅ Live Clock (every 30 seconds)
- Current time
- Date
- Day of week

### ⚠️ Home Assistant (needs config)
- Edit config.yaml
- Add your token
- Enable the widget

### ⚠️ Ubiquiti (needs config)
- Edit config.yaml
- Add controller credentials
- Enable the widget

---

## File Locations

Dashboard saves to:
- `emulator_output/preview.png` - RGB preview (view this!)
- `emulator_output/current.png` - 1-bit version
- `emulator_output/frame_*.png` - Frame history

Size: 1360×480 pixels (exact e-Paper display size)

---

## Troubleshooting

**"Dashboard not updating"**
- Check if python3 main_v2.py is running
- Check logs: `tail -f dashboard.log`
- Wait 60 seconds for next refresh

**"Preview not auto-refreshing"**
- Close and reopen the image in Preview
- Preview should auto-reload, but sometimes needs restart

**"Want faster updates"**
- Edit config.yaml: `refresh_interval: 30` (instead of 60)
- Restart dashboard

**"Image looks pixelated"**
- In Preview: Press **Cmd+0** for actual size
- The display is 1360×480, so it's wide and short

---

## Quick Commands

```bash
# EASIEST: Run dashboard + open Preview
./run_dashboard.sh

# Manual: Just dashboard
mv lib lib_disabled && python3 main_v2.py

# Manual: Just open image
open -a Preview emulator_output/preview.png

# Stop dashboard
# Press Ctrl+C in terminal where it's running

# Restore hardware driver (when done developing)
mv lib_disabled lib
```

---

## On Your Mac

Since you're on a Mac, the **best workflow** is:

1. Run: `./run_dashboard.sh`
2. Preview opens automatically
3. Position Preview window where you want
4. Dashboard updates every 60 seconds
5. Preview auto-refreshes to show changes
6. Press Ctrl+C in terminal to stop

**That's it!** Simple and native. 🎉

---

## When You Deploy to Raspberry Pi

On the Pi:
1. No emulator needed (uses real hardware)
2. No Preview app needed (displays on e-Paper)
3. Just run: `python3 main_v2.py`
4. Dashboard renders directly to e-Paper display

The code automatically detects the hardware and uses it!

---

Enjoy your live dashboard! 🚀
