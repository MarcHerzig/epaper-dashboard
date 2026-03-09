#!/bin/bash
# Setup script for ePaper Dashboard v2.0

echo "========================================="
echo "ePaper Dashboard v2.0 Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 not found. Please install Python 3.7 or later."
    exit 1
fi
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements_v2.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies."
    exit 1
fi
echo "✓ Dependencies installed"
echo ""

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo "ERROR: config.yaml not found!"
    echo "Please copy and edit config.yaml:"
    echo "  1. Edit the file with your API keys and settings"
    echo "  2. Configure your widgets"
    echo "  3. Run this script again"
    exit 1
fi
echo "✓ Configuration file found"
echo ""

# Validate YAML
echo "Validating configuration..."
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Invalid YAML syntax in config.yaml"
    echo "Please fix the syntax errors and try again"
    exit 1
fi
echo "✓ Configuration is valid"
echo ""

# Check for required directories
echo "Checking directories..."
for dir in widgets lib fnt icons; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: Directory $dir not found!"
        exit 1
    fi
done
echo "✓ All directories present"
echo ""

# Test import
echo "Testing widget system..."
python3 -c "from widgets.widget_manager import WidgetManager" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to import widget system"
    exit 1
fi
echo "✓ Widget system loads successfully"
echo ""

echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Edit config.yaml with your credentials"
echo "  2. Enable the widgets you want to use"
echo "  3. Run the dashboard:"
echo ""
echo "     python3 main_v2.py"
echo ""
echo "Or use tmux for persistent session:"
echo ""
echo "     tmux new -s dashboard"
echo "     python3 main_v2.py"
echo "     # Detach with Ctrl+B, then D"
echo ""
echo "View logs:"
echo "     tail -f dashboard.log"
echo ""
echo "========================================="
