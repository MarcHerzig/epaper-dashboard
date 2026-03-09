#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Widget Test Script
Test individual widgets without running the full dashboard
"""
import sys
import os
import yaml
import logging
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Setup paths
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, BASE_DIR)

# Import widget system
from widgets.widget_manager import WidgetManager
from widgets.base_widget import WidgetRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_test_config():
    """Load configuration for testing"""
    config_file = os.path.join(BASE_DIR, 'config.yaml')
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return None


def get_cached_icon(name, size, is_white=False):
    """Mock icon loader for testing"""
    icon_path = os.path.join(BASE_DIR, 'icons', f'{name}.bmp')
    if os.path.exists(icon_path):
        try:
            with Image.open(icon_path) as img:
                icon = img.convert("L").resize(size)
                icon = ImageOps.invert(icon)
                return icon.convert("1")
        except Exception as e:
            logger.warning(f"Failed to load icon {name}: {e}")
    return None


def load_test_fonts():
    """Load fonts for testing"""
    font_dir = os.path.join(BASE_DIR, 'fnt')

    def load_font(name, size):
        try:
            return ImageFont.truetype(os.path.join(font_dir, name), size)
        except Exception as e:
            logger.warning(f"Failed to load font {name} size {size}, using default")
            return ImageFont.load_default()

    return {
        '20': load_font('Aldrich-Regular.ttc', 20),
        '24': load_font('Aldrich-Regular.ttc', 24),
        '28': load_font('Aldrich-Regular.ttc', 28),
        '32': load_font('Aldrich-Regular.ttc', 32),
        '35': load_font('Aldrich-Regular.ttc', 35),
        '40': load_font('Aldrich-Regular.ttc', 40),
        '60': load_font('Aldrich-Regular.ttc', 60),
        '80': load_font('Aldrich-Regular.ttc', 80),
        'clock': load_font('advanced_led_board-7.ttc', 180),
    }


def test_widget_discovery():
    """Test that widgets are discovered and registered"""
    print("\n" + "=" * 60)
    print("TEST: Widget Discovery")
    print("=" * 60)

    from widgets.widget_manager import WidgetManager

    # This will trigger widget discovery
    config = {'widgets': []}
    manager = WidgetManager(config)

    registered = WidgetRegistry.list_widgets()
    print(f"✓ Discovered {len(registered)} widgets:")
    for widget_name in registered:
        print(f"  - {widget_name}")

    return len(registered) > 0


def test_config_validation():
    """Test configuration loading and validation"""
    print("\n" + "=" * 60)
    print("TEST: Configuration Validation")
    print("=" * 60)

    config = load_test_config()
    if not config:
        print("✗ Failed to load config.yaml")
        return False

    print("✓ Configuration loaded successfully")

    # Check required sections
    required_sections = ['display', 'widgets']
    for section in required_sections:
        if section in config:
            print(f"✓ Section '{section}' found")
        else:
            print(f"✗ Section '{section}' missing")
            return False

    # Check display config
    display = config.get('display', {})
    if display.get('width') == 1360 and display.get('height') == 480:
        print(f"✓ Display resolution: {display['width']}x{display['height']}")
    else:
        print(f"⚠ Non-standard resolution: {display.get('width')}x{display.get('height')}")

    # Check widgets
    widgets = config.get('widgets', [])
    enabled_count = sum(1 for w in widgets if w.get('enabled', False))
    print(f"✓ Found {len(widgets)} widgets ({enabled_count} enabled)")

    return True


def test_widget_initialization(widget_name=None):
    """Test widget initialization"""
    print("\n" + "=" * 60)
    print(f"TEST: Widget Initialization" + (f" ({widget_name})" if widget_name else " (all enabled)"))
    print("=" * 60)

    config = load_test_config()
    if not config:
        return False

    manager = WidgetManager(config)
    manager.load_widgets()

    if len(manager.widgets) == 0:
        print("✗ No widgets loaded (all may be disabled)")
        return False

    print(f"✓ Loaded {len(manager.widgets)} widgets:")
    for widget in manager.widgets:
        print(f"  - {widget.__class__.__name__} at {widget.position}")

    return True


def test_widget_data_fetch(widget_type=None):
    """Test fetching data from a specific widget type"""
    print("\n" + "=" * 60)
    print(f"TEST: Widget Data Fetch" + (f" ({widget_type})" if widget_type else ""))
    print("=" * 60)

    config = load_test_config()
    if not config:
        return False

    manager = WidgetManager(config)
    manager.load_widgets()

    success = True
    for widget in manager.widgets:
        if widget_type and widget.__class__.__name__.lower() != widget_type.lower() + 'widget':
            continue

        print(f"\nTesting {widget.__class__.__name__}...")
        try:
            data = widget.fetch_data()
            if data is not None:
                print(f"  ✓ Fetched data successfully")
                print(f"  Data keys: {list(data.keys())}")
            else:
                print(f"  ⚠ No data returned (may be expected if APIs not configured)")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            success = False

    return success


def test_widget_rendering():
    """Test rendering all widgets to an image"""
    print("\n" + "=" * 60)
    print("TEST: Widget Rendering")
    print("=" * 60)

    config = load_test_config()
    if not config:
        return False

    # Load fonts
    fonts = load_test_fonts()

    # Create manager and load widgets
    manager = WidgetManager(config)
    manager.load_widgets()

    if len(manager.widgets) == 0:
        print("✗ No widgets to render")
        return False

    # Create test image
    display_config = config.get('display', {})
    width = display_config.get('width', 1360)
    height = display_config.get('height', 480)

    image = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(image)

    # Render all widgets
    try:
        manager.render_all(draw, fonts, get_cached_icon)
        print(f"✓ Rendered {len(manager.widgets)} widgets successfully")

        # Save test output
        output_dir = os.path.join(BASE_DIR, 'test_output')
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, 'test_render.png')
        image.save(output_file)
        print(f"✓ Saved test render to: {output_file}")

        # Also save RGB version for easier viewing
        rgb_output = os.path.join(output_dir, 'test_render_preview.png')
        image.convert('RGB').save(rgb_output)
        print(f"✓ Saved preview to: {rgb_output}")

        return True

    except Exception as e:
        print(f"✗ Rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING ALL WIDGET TESTS")
    print("=" * 60)

    tests = [
        ("Widget Discovery", test_widget_discovery),
        ("Configuration Validation", test_config_validation),
        ("Widget Initialization", test_widget_initialization),
        ("Widget Rendering", test_widget_rendering),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return passed == total


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test dashboard widgets')
    parser.add_argument('--test', choices=['all', 'discovery', 'config', 'init', 'fetch', 'render'],
                        default='all', help='Which test to run')
    parser.add_argument('--widget', help='Test specific widget type (e.g., weather, homeassistant)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.test == 'all':
            success = run_all_tests()
        elif args.test == 'discovery':
            success = test_widget_discovery()
        elif args.test == 'config':
            success = test_config_validation()
        elif args.test == 'init':
            success = test_widget_initialization(args.widget)
        elif args.test == 'fetch':
            success = test_widget_data_fetch(args.widget)
        elif args.test == 'render':
            success = test_widget_rendering()
        else:
            success = run_all_tests()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(130)
