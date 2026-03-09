#!/bin/bash
# Run dashboard with emulator (for development on Mac/Linux/Windows)

echo "============================================"
echo "Starting ePaper Dashboard with Emulator"
echo "============================================"
echo ""

# Temporarily disable hardware driver to force emulator mode
if [ -d "lib" ]; then
    echo "Disabling hardware driver (will restore on exit)..."
    mv lib lib_hardware_disabled
    RESTORE_LIB=1
fi

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping dashboard..."
    if [ ! -z "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null
    fi

    # Restore hardware driver
    if [ "$RESTORE_LIB" = "1" ] && [ -d "lib_hardware_disabled" ]; then
        echo "Restoring hardware driver..."
        mv lib_hardware_disabled lib
    fi

    echo "Dashboard stopped."
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Run dashboard
echo "Starting dashboard..."
echo "Press Ctrl+C to stop"
echo ""
echo "Output will be saved to: emulator_output/preview.png"
echo "You can view it with: open emulator_output/preview.png"
echo ""
echo "============================================"
echo ""

python3 main_v2.py &
DASHBOARD_PID=$!

# Wait for dashboard process
wait $DASHBOARD_PID

cleanup
