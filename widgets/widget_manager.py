"""Widget manager for loading and managing dashboard widgets"""
import os
import logging
import importlib
from typing import List, Dict, Any
from .base_widget import WidgetRegistry, BaseWidget


logger = logging.getLogger('widget_manager')


class WidgetManager:
    """
    Manages loading, initializing, and coordinating all dashboard widgets
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize widget manager

        Args:
            config: Full configuration dictionary from config.yaml
        """
        self.config = config
        self.widgets: List[BaseWidget] = []
        self._discover_widgets()

    def _discover_widgets(self):
        """Automatically import all widget modules to register them"""
        widgets_dir = os.path.dirname(__file__)

        for filename in os.listdir(widgets_dir):
            if filename.endswith('_widget.py'):
                module_name = filename[:-3]  # Remove .py
                try:
                    importlib.import_module(f'widgets.{module_name}')
                    logger.debug(f"Loaded widget module: {module_name}")
                except Exception as e:
                    logger.error(f"Failed to load widget module {module_name}: {e}")

        logger.info(f"Discovered widgets: {WidgetRegistry.list_widgets()}")

    def load_widgets(self):
        """
        Load and initialize all enabled widgets from configuration
        """
        widget_configs = self.config.get('widgets', [])

        for widget_config in widget_configs:
            if not widget_config.get('enabled', True):
                logger.info(f"Widget '{widget_config['name']}' is disabled, skipping")
                continue

            widget_type = widget_config['type']
            widget_class = WidgetRegistry.get_widget(widget_type)

            if not widget_class:
                logger.error(f"Unknown widget type: {widget_type}")
                continue

            try:
                # Extract position and size
                position = tuple(widget_config['position'])
                size = tuple(widget_config['size'])

                # Create widget instance
                widget = widget_class(widget_config, position, size)
                self.widgets.append(widget)

                logger.info(f"Loaded widget: {widget_config['name']} ({widget_type}) at {position}")

            except Exception as e:
                logger.error(f"Failed to initialize widget '{widget_config['name']}': {e}")

        logger.info(f"Loaded {len(self.widgets)} widgets successfully")

    def start_all(self):
        """Start update threads for all widgets"""
        for widget in self.widgets:
            try:
                widget.start_update_thread()
            except Exception as e:
                logger.error(f"Failed to start widget {widget.__class__.__name__}: {e}")

    def stop_all(self):
        """Stop all widget update threads"""
        for widget in self.widgets:
            try:
                widget.stop_update_thread()
            except Exception as e:
                logger.error(f"Failed to stop widget {widget.__class__.__name__}: {e}")

    def render_all(self, draw, fonts, icon_loader):
        """
        Render all widgets on the display

        Args:
            draw: PIL ImageDraw object
            fonts: Dictionary of loaded fonts
            icon_loader: Function to load icons
        """
        for widget in self.widgets:
            try:
                widget.render(draw, fonts, icon_loader)
            except Exception as e:
                logger.error(f"Failed to render widget {widget.__class__.__name__}: {e}")
                # Draw error indicator
                widget.draw_error(draw, "ERR")

    def get_widget_by_name(self, name: str) -> BaseWidget:
        """Get a widget instance by its configured name"""
        for widget in self.widgets:
            if hasattr(widget, 'name') and widget.name == name:
                return widget
        return None
