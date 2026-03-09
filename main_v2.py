#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Modular ePaper Dashboard v2.0
Widget-based architecture for easy extensibility
"""
import sys
import os
import time
import logging
import signal
import gc
import yaml
from PIL import Image, ImageDraw, ImageFont, ImageOps
from logging.handlers import RotatingFileHandler

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
LIB_DIR = os.path.join(BASE_DIR, 'lib')
FONT_DIR = os.path.join(BASE_DIR, 'fnt')
ICON_DIR = os.path.join(BASE_DIR, 'icons')
LOG_FILE = os.path.join(BASE_DIR, 'dashboard.log')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.yaml')

if os.path.exists(LIB_DIR):
    sys.path.append(LIB_DIR)

# Try to import real hardware driver, fall back to emulator
try:
    from waveshare_epd import epd10in85
    logger = logging.getLogger(__name__)
    logger.info("Using real Waveshare epd10in85 hardware driver")
except ImportError:
    # Use emulator for development
    try:
        from emulator import epd10in85
        print("=" * 60)
        print("RUNNING IN EMULATOR MODE")
        print("No hardware detected - using display emulator")
        print("Output will be saved to emulator_output/ directory")
        print("=" * 60)
    except ImportError:
        epd10in85 = None
        print("ERROR: Neither hardware driver nor emulator found!")

# Import widget system
from widgets.widget_manager import WidgetManager

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=2)
file_handler.setFormatter(formatter)

logger.handlers.clear()
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# --- GLOBALS ---
icon_cache = {}
config = None


class HardwareTimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise HardwareTimeoutError("Hardware Busy-Wait Timeout")


def load_config():
    """Load configuration from YAML file"""
    global config
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {CONFIG_FILE}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {CONFIG_FILE}")
        logger.error("Please create config.yaml based on config.yaml.example")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)


def get_config():
    """Get the current configuration"""
    return config


def get_cached_icon(name, size, is_white=False):
    """Load and cache icons"""
    key = f"{name}_{size[0]}x{size[1]}_{'white' if is_white else 'black'}"
    if key not in icon_cache:
        path = os.path.join(ICON_DIR, f"{name}.bmp")
        if os.path.exists(path):
            try:
                with Image.open(path) as f_img:
                    img = f_img.convert("L").resize(size)
                    img = ImageOps.invert(img)
                    icon_cache[key] = img.convert("1")
            except Exception as e:
                logger.warning(f"Failed to load icon {name}: {e}")
                return None
        else:
            logger.debug(f"Icon not found: {path}")
            icon_cache[key] = None
    return icon_cache.get(key)


def load_fonts():
    """Load all required fonts"""
    def load_font(name, size):
        try:
            return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
        except Exception as e:
            logger.error(f"Failed to load font {name} size {size}: {e}")
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


def render_screen(widget_manager, display_config, fonts):
    """Render all widgets on the screen"""
    width = display_config.get('width', 1360)
    height = display_config.get('height', 480)

    # Create blank image
    image = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(image)

    # Render all widgets
    widget_manager.render_all(draw, fonts, get_cached_icon)

    return image


def main():
    """Main application loop"""
    # Load configuration
    cfg = load_config()
    display_config = cfg.get('display', {})

    # Set up signal handler for hardware timeout
    signal.signal(signal.SIGALRM, timeout_handler)

    # Initialize display
    epd = None
    if epd10in85:
        try:
            epd = epd10in85.EPD()
            epd.init()
            epd.Clear()
            time.sleep(1)
            epd.init_Part()
            logger.info("Display initialized")
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            sys.exit(1)
    else:
        logger.warning("Running in simulation mode (no display)")

    # Load fonts
    fonts = load_fonts()

    # Initialize widget manager
    widget_manager = WidgetManager(cfg)
    widget_manager.load_widgets()

    # Start all widget update threads
    widget_manager.start_all()
    logger.info("All widgets started")

    # Main render loop
    refresh_counter = 0
    refresh_interval = display_config.get('refresh_interval', 60)
    full_refresh_cycles = display_config.get('full_refresh_cycles', 600)

    try:
        while True:
            start_time = time.time()

            try:
                # Set hardware timeout alarm
                if epd:
                    signal.alarm(20)

                # Render screen
                image = render_screen(widget_manager, display_config, fonts)

                # Update display
                if epd:
                    buf = epd.getbuffer(image)

                    if refresh_counter >= full_refresh_cycles:
                        logger.info("Full refresh cycle")
                        epd.init()
                        epd.display(buf)
                        time.sleep(2)
                        epd.init_Part()
                        refresh_counter = 0
                    else:
                        logger.info(f"Partial refresh ({refresh_counter}/{full_refresh_cycles})")
                        epd.display_Partial(buf, 0, 0, epd.width, epd.height)
                        refresh_counter += 1

                    signal.alarm(0)
                    del buf

                del image

                # Periodic garbage collection
                if refresh_counter % 10 == 0:
                    gc.collect()

            except HardwareTimeoutError:
                logger.critical("HARDWARE HANG DETECTED! Restarting...")
                signal.alarm(0)
                logging.shutdown()
                os.execv(sys.executable, ['python3'] + sys.argv)

            except OSError as e:
                signal.alarm(0)
                if e.errno == 24:  # Too many open files
                    logger.error("Too many open files, restarting...")
                    os.execv(sys.executable, ['python3'] + sys.argv)
                else:
                    raise

            except Exception as e:
                signal.alarm(0)
                logger.error(f"Error in main loop: {e}", exc_info=True)

            # Sleep until next refresh
            elapsed = time.time() - start_time
            sleep_time = max(5, refresh_interval - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        signal.alarm(0)
        widget_manager.stop_all()
        if epd:
            try:
                epd10in85.epdconfig.module_exit(cleanup=True)
            except:
                pass
        sys.exit(0)


if __name__ == '__main__':
    main()
