#!/bin/bash
# Run dashboard with emulator AND web viewer for live preview

echo "============================================"
echo "ePaper Dashboard - Live Development Mode"
echo "============================================"
echo ""

# Check if running on Mac
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac - disable hardware driver
    if [ -d "lib" ]; then
        mv lib lib_hardware_disabled 2>/dev/null
    fi
fi

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping services..."

    # Kill dashboard
    if [ ! -z "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null
        echo "  ✓ Dashboard stopped"
    fi

    # Kill viewer
    if [ ! -z "$VIEWER_PID" ]; then
        kill $VIEWER_PID 2>/dev/null
        echo "  ✓ Viewer stopped"
    fi

    # Restore hardware driver on Mac
    if [[ "$OSTYPE" == "darwin"* ]] && [ -d "lib_hardware_disabled" ]; then
        mv lib_hardware_disabled lib 2>/dev/null
    fi

    echo ""
    echo "Shutdown complete!"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start dashboard in background
echo "Starting dashboard..."
python3 main_v2.py > /dev/null 2>&1 &
DASHBOARD_PID=$!
echo "  ✓ Dashboard running (PID: $DASHBOARD_PID)"

# Wait a moment for dashboard to initialize
sleep 2

# Start viewer in background
echo "Starting web viewer..."
python3 viewer.py > /dev/null 2>&1 &
VIEWER_PID=$!
echo "  ✓ Viewer running (PID: $VIEWER_PID)"

echo ""
echo "============================================"
echo "✓ Dashboard is running!"
echo "============================================"
echo ""
echo "View dashboard at: http://localhost:8080"
echo "Files are saved to: emulator_output/preview.png"
echo ""
echo "The viewer auto-refreshes every 2 seconds"
echo "Dashboard updates every 60 seconds"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for user interrupt
wait $DASHBOARD_PID

cleanup
