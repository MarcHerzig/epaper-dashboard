#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Live Dashboard Viewer - Shows the dashboard in a real-time updating window
Exact size: 1360x480 (same as the e-Paper display)
"""
import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import threading


class LiveDashboardViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("ePaper Dashboard - Live View (1360×480)")

        # Set exact window size
        self.width = 1360
        self.height = 480

        # Configure window
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(False, False)

        # Create canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg='white', highlightthickness=0)
        self.canvas.pack()

        # Status bar
        self.status_frame = tk.Frame(root, bg='#2a2a2a', height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = tk.Label(
            self.status_frame,
            text="⚪ Initializing...",
            bg='#2a2a2a',
            fg='#00ff00',
            font=('Courier', 10),
            anchor='w',
            padx=10
        )
        self.status_label.pack(fill=tk.X)

        # Image path
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.image_path = os.path.join(self.base_dir, 'emulator_output', 'preview.png')

        # Current image reference
        self.current_image = None
        self.photo_image = None
        self.last_modified = 0
        self.update_count = 0

        # Auto-refresh
        self.running = True
        self.refresh_interval = 1000  # milliseconds

        # Start update loop
        self.update_display()

    def update_display(self):
        """Update the display if the image has changed"""
        try:
            if os.path.exists(self.image_path):
                # Check if file has been modified
                current_modified = os.path.getmtime(self.image_path)

                if current_modified != self.last_modified:
                    # Load new image
                    image = Image.open(self.image_path)

                    # Resize to exact window size if needed
                    if image.size != (self.width, self.height):
                        image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

                    # Convert to PhotoImage
                    self.photo_image = ImageTk.PhotoImage(image)

                    # Clear canvas and draw new image
                    self.canvas.delete("all")
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

                    # Update status
                    self.last_modified = current_modified
                    self.update_count += 1
                    timestamp = time.strftime("%H:%M:%S")
                    self.status_label.config(
                        text=f"🟢 LIVE - Last update: {timestamp} | Updates: {self.update_count}",
                        fg='#00ff00'
                    )
                else:
                    # No change
                    timestamp = time.strftime("%H:%M:%S")
                    self.status_label.config(
                        text=f"⚪ Waiting for update... ({timestamp}) | Updates: {self.update_count}",
                        fg='#ffaa00'
                    )
            else:
                self.status_label.config(
                    text="🔴 No dashboard image found - Start main_v2.py first!",
                    fg='#ff0000'
                )
        except Exception as e:
            self.status_label.config(
                text=f"⚠️ Error: {str(e)}",
                fg='#ff0000'
            )

        # Schedule next update
        if self.running:
            self.root.after(self.refresh_interval, self.update_display)

    def on_closing(self):
        """Handle window close"""
        self.running = False
        self.root.destroy()


def main():
    print("=" * 60)
    print("ePaper Dashboard - Live Viewer")
    print("=" * 60)
    print()
    print("Window size: 1360×480 (exact e-Paper display size)")
    print("Auto-refresh: Every 1 second")
    print()
    print("Instructions:")
    print("  1. Keep this window open")
    print("  2. Run: python3 main_v2.py (in another terminal)")
    print("  3. Watch the dashboard update live!")
    print()
    print("Press Ctrl+C or close window to exit")
    print("=" * 60)
    print()

    root = tk.Tk()
    app = LiveDashboardViewer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nViewer stopped.")


if __name__ == '__main__':
    main()
