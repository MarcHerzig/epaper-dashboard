#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
ePaper Display Emulator
Simulates the Waveshare 10.85" e-Paper display (1360x480) for development without hardware
"""
import os
import time
from PIL import Image


class EPD:
    """Emulated EPD (E-Paper Display) class"""

    def __init__(self):
        self.width = 1360
        self.height = 480
        self.output_dir = os.path.join(os.path.dirname(__file__), 'emulator_output')
        self.frame_count = 0
        self.last_image = None

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"[EMULATOR] Initialized {self.width}x{self.height} display emulator")
        print(f"[EMULATOR] Output directory: {self.output_dir}")

    def init(self):
        """Initialize display (full refresh mode)"""
        print("[EMULATOR] Display init() - Full refresh mode")
        time.sleep(0.1)  # Simulate initialization delay

    def init_Part(self):
        """Initialize partial refresh mode"""
        print("[EMULATOR] Display init_Part() - Partial refresh mode")
        time.sleep(0.05)

    def Clear(self):
        """Clear the display"""
        print("[EMULATOR] Clearing display")
        # Create blank white image
        blank = Image.new('1', (self.width, self.height), 255)
        self.last_image = blank
        self._save_image(blank, "cleared")

    def getbuffer(self, image):
        """Convert image to display buffer format"""
        # In the real hardware, this converts PIL Image to bytes
        # For emulator, we just return the image
        return image

    def display(self, buffer):
        """Full refresh display update"""
        print("[EMULATOR] Full refresh display update")
        self.last_image = buffer
        self._save_image(buffer, "full_refresh")
        time.sleep(0.5)  # Simulate refresh time

    def display_Partial(self, buffer, x, y, w, h):
        """Partial refresh display update"""
        print(f"[EMULATOR] Partial refresh at ({x}, {y}) size {w}x{h}")
        self.last_image = buffer
        self._save_image(buffer, "partial_refresh")
        time.sleep(0.2)  # Simulate faster partial refresh

    def sleep(self):
        """Put display to sleep"""
        print("[EMULATOR] Display entering sleep mode")

    def _save_image(self, image, mode):
        """Save the current image to disk"""
        # Save current frame
        current_file = os.path.join(self.output_dir, 'current.png')
        image.save(current_file)

        # Also save numbered frame for history
        frame_file = os.path.join(self.output_dir, f'frame_{self.frame_count:04d}_{mode}.png')
        image.save(frame_file)

        self.frame_count += 1

        # Save preview with better contrast for viewing
        preview_file = os.path.join(self.output_dir, 'preview.png')
        # Convert 1-bit to RGB for better viewing
        rgb_image = image.convert('RGB')
        rgb_image.save(preview_file)

        print(f"[EMULATOR] Saved: {current_file}")


class epdconfig:
    """Emulated epdconfig module"""

    @staticmethod
    def module_init():
        print("[EMULATOR] Module init")
        return 0

    @staticmethod
    def module_exit(cleanup=True):
        print(f"[EMULATOR] Module exit (cleanup={cleanup})")


# Create a mock epd10in85 module for import
class MockEPD10in85Module:
    EPD = EPD
    epdconfig = epdconfig


# Export for use in main_v2.py
epd10in85 = MockEPD10in85Module()


if __name__ == '__main__':
    """Test the emulator"""
    from PIL import ImageDraw, ImageFont

    print("Testing EPD Emulator...")
    print("=" * 50)

    # Initialize display
    epd = EPD()
    epd.init()
    epd.Clear()

    # Create test image
    image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)

    # Try to load a font, fallback to default
    try:
        font_large = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 60)
        font_medium = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 30)
        font_small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 20)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw test pattern
    # Header
    draw.rectangle((0, 0, epd.width, 80), fill=0)
    draw.text((20, 10), "ePaper Display Emulator Test", font=font_large, fill=255)

    # Info
    draw.text((20, 100), f"Resolution: {epd.width} x {epd.height}", font=font_medium, fill=0)
    draw.text((20, 140), "Waveshare 10.85\" E-Paper Display", font=font_small, fill=0)

    # Grid pattern
    draw.text((20, 200), "Grid Test Pattern:", font=font_medium, fill=0)
    for i in range(0, epd.width, 100):
        draw.line((i, 250, i, 350), fill=0, width=1)
    for i in range(250, 350, 20):
        draw.line((0, i, epd.width, i), fill=0, width=1)

    # Shapes
    draw.text((20, 370), "Shape Tests:", font=font_medium, fill=0)
    draw.rectangle((20, 410, 120, 460), outline=0, width=3)
    draw.ellipse((140, 410, 240, 460), outline=0, width=3)
    draw.polygon([(260, 460), (310, 410), (360, 460)], outline=0, width=3)

    # Text alignment test
    draw.text((epd.width - 400, 370), "Text Alignment:", font=font_medium, fill=0)
    draw.text((epd.width - 400, 410), "Left aligned", font=font_small, fill=0)
    text = "Right aligned"
    try:
        bbox = draw.textbbox((0, 0), text, font=font_small)
        text_width = bbox[2] - bbox[0]
    except AttributeError:
        text_width = draw.textsize(text, font=font_small)[0]
    draw.text((epd.width - 20 - text_width, 435), text, font=font_small, fill=0)

    # Display the test pattern
    epd.init_Part()
    buf = epd.getbuffer(image)
    epd.display(buf)

    print("=" * 50)
    print("Test complete!")
    print(f"Check the output in: {epd.output_dir}")
    print("Files created:")
    print("  - current.png    : Latest display state")
    print("  - preview.png    : RGB preview (easier to view)")
    print("  - frame_*.png    : Frame history")
