#!/bin/bash
# Run dashboard with auto-updating Preview window (Mac native!)

echo "============================================"
echo "ePaper Dashboard - Mac Preview Mode"
echo "============================================"
echo ""

# Disable hardware driver on Mac
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -d "lib" ]; then
        mv lib lib_disabled 2>/dev/null
        RESTORE_LIB=1
    fi
fi

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping dashboard..."

    if [ ! -z "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null
        wait $DASHBOARD_PID 2>/dev/null
        echo "  ✓ Dashboard stopped"
    fi

    # Restore hardware driver
    if [ "$RESTORE_LIB" = "1" ] && [ -d "lib_disabled" ]; then
        mv lib_disabled lib 2>/dev/null
    fi

    echo ""
    echo "Shutdown complete!"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start dashboard in background
echo "Starting dashboard..."
python3 main_v2.py &
DASHBOARD_PID=$!
echo "  ✓ Dashboard running (PID: $DASHBOARD_PID)"
echo ""

# Wait for first image
echo "Waiting for first render..."
for i in {1..20}; do
    if [ -f "emulator_output/preview.png" ]; then
        echo "  ✓ First frame ready!"
        break
    fi
    sleep 1
done
echo ""

# Open with Preview app (Mac auto-refreshes!)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Opening Preview app..."
    open -a Preview emulator_output/preview.png
    echo ""
    echo "============================================"
    echo "✓ DASHBOARD RUNNING"
    echo "============================================"
    echo ""
    echo "The Preview window will auto-refresh!"
    echo ""
    echo "Dashboard updates: Every 60 seconds"
    echo "Image size: 1360×480 pixels"
    echo ""
    echo "In Preview app:"
    echo "  • Press Cmd+0 for actual size (1:1)"
    echo "  • Press Cmd+1 to fit to window"
    echo "  • The image auto-updates when dashboard refreshes"
    echo ""
    echo "Press Ctrl+C here to stop the dashboard"
    echo ""
    echo "============================================"
else
    echo "Open the image: emulator_output/preview.png"
    echo "It updates every 60 seconds"
fi

# Wait for dashboard
wait $DASHBOARD_PID

cleanup
