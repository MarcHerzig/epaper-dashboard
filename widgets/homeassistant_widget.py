"""Home Assistant widget for ePaper dashboard"""
import requests
from typing import Dict, Any, Optional
from .base_widget import BaseWidget, WidgetRegistry


@WidgetRegistry.register('homeassistant')
class HomeAssistantWidget(BaseWidget):
    """
    Display Home Assistant entities (sensors, lights, switches, energy)

    Config options:
        url: Home Assistant URL (e.g., "http://homeassistant.local:8123")
        token: Long-lived access token
        entities: List of entities to display
            - entity_id: HA entity ID (e.g., "sensor.temperature")
            - display_name: Name to show on display
            - icon: Icon name (optional)
            - unit: Unit override (optional)
    """

    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.base_url = config['config']['url'].rstrip('/')
        self.token = config['config']['token']
        self.entities = config['config'].get('entities', [])
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        })

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch state of all configured entities from Home Assistant"""
        entity_states = []

        for entity_config in self.entities:
            entity_id = entity_config['entity_id']
            try:
                url = f"{self.base_url}/api/states/{entity_id}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                state_data = response.json()

                # Extract relevant info
                state = state_data.get('state', 'unknown')
                attributes = state_data.get('attributes', {})
                unit = entity_config.get('unit') or attributes.get('unit_of_measurement', '')

                entity_states.append({
                    'entity_id': entity_id,
                    'display_name': entity_config.get('display_name', entity_id),
                    'state': state,
                    'unit': unit,
                    'icon': entity_config.get('icon', 'icon_home'),
                    'friendly_name': attributes.get('friendly_name', ''),
                    'device_class': attributes.get('device_class', ''),
                })

            except Exception as e:
                self.logger.error(f"Failed to fetch {entity_id}: {e}")
                entity_states.append({
                    'entity_id': entity_id,
                    'display_name': entity_config.get('display_name', entity_id),
                    'state': 'unavailable',
                    'unit': '',
                    'icon': entity_config.get('icon', 'icon_home'),
                })

        return {
            'entities': entity_states,
            'timestamp': self.last_update,
        }

    def render(self, draw, fonts, icon_loader):
        """Render Home Assistant entities on the display"""
        data = self.get_data()
        if not data or 'entities' not in data:
            self.draw_loading(draw)
            return

        x, y = self.position
        width, height = self.size

        # Header
        draw.text((x, y), "HOME ASSISTANT", font=fonts['28'], fill=0)

        # Draw entities in a grid or list
        entities = data['entities']
        y_offset = y + 40
        row_height = 35

        for i, entity in enumerate(entities[:4]):  # Limit to 4 entities for space
            entity_y = y_offset + (i * row_height)

            # Icon
            icon = entity.get('icon', 'icon_home')
            icon_img = icon_loader(icon, (30, 30))
            if icon_img:
                draw.bitmap((x, entity_y), icon_img, fill=0)

            # Name and state
            name = entity['display_name']
            state = entity['state']
            unit = entity['unit']

            # Format state based on type
            if state in ['on', 'off']:
                state_text = state.upper()
            elif state == 'unavailable':
                state_text = "N/A"
            else:
                try:
                    # Try to format as number
                    state_val = float(state)
                    state_text = f"{state_val:.1f}{unit}"
                except ValueError:
                    state_text = f"{state}{unit}"

            # Draw name and state
            draw.text((x + 40, entity_y), f"{name}:", font=fonts['20'], fill=0)

            # Right-align state value
            try:
                bbox = draw.textbbox((0, 0), state_text, font=fonts['24'])
                text_width = bbox[2] - bbox[0]
            except AttributeError:
                text_width = draw.textsize(state_text, font=fonts['24'])[0]

            state_x = x + width - text_width - 10
            draw.text((state_x, entity_y - 2), state_text, font=fonts['24'], fill=0)

        # Optional: Draw connection status indicator
        if data.get('timestamp', 0) > 0:
            # Small dot to indicate active connection
            draw.ellipse((x + width - 20, y + 5, x + width - 10, y + 15), fill=0)
