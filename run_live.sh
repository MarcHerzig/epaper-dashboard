#!/bin/bash
# Run dashboard with LIVE GUI viewer window (1360x480)

echo "============================================"
echo "ePaper Dashboard - LIVE Window View"
echo "============================================"
echo ""

# Disable hardware driver on Mac
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -d "lib" ]; then
        mv lib lib_disabled 2>/dev/null
    fi
fi

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping dashboard and viewer..."

    if [ ! -z "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null
        echo "  ✓ Dashboard stopped"
    fi

    if [ ! -z "$VIEWER_PID" ]; then
        kill $VIEWER_PID 2>/dev/null
        echo "  ✓ Viewer stopped"
    fi

    # Restore hardware driver
    if [[ "$OSTYPE" == "darwin"* ]] && [ -d "lib_disabled" ]; then
        mv lib_disabled lib 2>/dev/null
    fi

    echo ""
    echo "Shutdown complete!"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start dashboard in background
echo "Starting dashboard..."
python3 main_v2.py > /dev/null 2>&1 &
DASHBOARD_PID=$!
echo "  ✓ Dashboard running (PID: $DASHBOARD_PID)"
echo ""

# Wait for first image to be created
echo "Waiting for dashboard to render first frame..."
for i in {1..15}; do
    if [ -f "emulator_output/preview.png" ]; then
        echo "  ✓ First frame ready!"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Start live viewer window
echo "Opening live viewer window (1360x480)..."
echo ""
echo "============================================"
echo "✓ LIVE VIEWER RUNNING"
echo "============================================"
echo ""
echo "A window will open showing the dashboard"
echo "Window size: 1360×480 (exact e-Paper size)"
echo "Updates: Every 1 second automatically"
echo ""
echo "Keep this terminal open"
echo "Press Ctrl+C to stop everything"
echo ""

python3 live_viewer.py &
VIEWER_PID=$!

# Wait for viewer
wait $VIEWER_PID

cleanup
