"""Base widget class and registry for ePaper dashboard"""
import threading
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple


class WidgetRegistry:
    """Central registry for all available widgets"""
    _widgets = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a widget class"""
        def decorator(widget_class):
            cls._widgets[name] = widget_class
            return widget_class
        return decorator

    @classmethod
    def get_widget(cls, name: str):
        """Get a widget class by name"""
        return cls._widgets.get(name)

    @classmethod
    def list_widgets(cls):
        """List all registered widget names"""
        return list(cls._widgets.keys())


class BaseWidget(ABC):
    """
    Abstract base class for all dashboard widgets.

    Each widget must implement:
    - fetch_data(): Retrieve data from external source
    - render(): Draw the widget on the display
    """

    def __init__(self, config: Dict[str, Any], position: Tuple[int, int], size: Tuple[int, int]):
        """
        Initialize widget

        Args:
            config: Widget-specific configuration from config.yaml
            position: (x, y) position on screen
            size: (width, height) of widget area
        """
        self.config = config
        self.position = position
        self.size = size
        self.data = {}
        self.lock = threading.Lock()
        self.last_update = 0
        self.update_interval = config.get('update_interval', 300)  # Default 5 minutes
        self.enabled = config.get('enabled', True)
        self.logger = logging.getLogger(f"widget.{self.__class__.__name__}")

        # Thread management
        self._thread = None
        self._stop_event = threading.Event()

    @abstractmethod
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch data from external source (API, database, etc.)

        Returns:
            Dictionary with widget data, or None on failure
        """
        pass

    @abstractmethod
    def render(self, draw, fonts: Dict[str, Any], icon_loader) -> None:
        """
        Render the widget on the display

        Args:
            draw: PIL ImageDraw object
            fonts: Dictionary of loaded fonts
            icon_loader: Function to load icons: icon_loader(name, size, is_white=False)
        """
        pass

    def get_data(self) -> Dict[str, Any]:
        """Thread-safe data getter"""
        with self.lock:
            return self.data.copy()

    def set_data(self, data: Dict[str, Any]) -> None:
        """Thread-safe data setter"""
        with self.lock:
            self.data = data
            self.last_update = time.time()

    def start_update_thread(self):
        """Start background thread for data updates"""
        if not self.enabled:
            self.logger.info(f"{self.__class__.__name__} is disabled")
            return

        if self._thread and self._thread.is_alive():
            self.logger.warning(f"{self.__class__.__name__} thread already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()
        self.logger.info(f"{self.__class__.__name__} update thread started")

    def stop_update_thread(self):
        """Stop the background update thread"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _update_loop(self):
        """Internal update loop - runs in background thread"""
        # Stagger initial fetch to avoid startup spike
        initial_delay = self.config.get('initial_delay', 0)
        if initial_delay > 0:
            time.sleep(initial_delay)

        while not self._stop_event.is_set():
            try:
                self.logger.debug(f"Fetching data for {self.__class__.__name__}")
                data = self.fetch_data()
                if data is not None:
                    self.set_data(data)
                    self.logger.debug(f"Data updated for {self.__class__.__name__}")
                else:
                    self.logger.warning(f"Failed to fetch data for {self.__class__.__name__}")
            except Exception as e:
                self.logger.error(f"Error fetching data for {self.__class__.__name__}: {e}")

            # Wait for next update
            self._stop_event.wait(self.update_interval)

    def draw_error(self, draw, message: str = "ERROR"):
        """Helper to draw error state"""
        x, y = self.position
        draw.rectangle((x, y, x + 100, y + 50), outline=0)
        draw.text((x + 10, y + 15), message, fill=0)

    def draw_loading(self, draw):
        """Helper to draw loading state"""
        x, y = self.position
        draw.text((x + 10, y + 15), "Loading...", fill=0)
