# Widget Ideas & Implementation Guide

Quick reference for implementing common home automation and network widgets.

---

## 1. Pi-hole DNS Stats

```python
"""Pi-hole widget"""
import requests
from .base_widget import BaseWidget, WidgetRegistry

@WidgetRegistry.register('pihole')
class PiHoleWidget(BaseWidget):
    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.pihole_url = config['config']['url']
        self.api_token = config['config'].get('api_token', '')

    def fetch_data(self):
        try:
            url = f"{self.pihole_url}/admin/api.php"
            params = {'summaryRaw': '', 'auth': self.api_token}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch Pi-hole data: {e}")
            return None

    def render(self, draw, fonts, icon_loader):
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        draw.text((x, y), "PI-HOLE", font=fonts['28'], fill=0)
        draw.text((x, y + 40), f"Blocked: {data.get('ads_blocked_today', 0)}", font=fonts['20'], fill=0)
        draw.text((x, y + 65), f"Queries: {data.get('dns_queries_today', 0)}", font=fonts['20'], fill=0)
        percent = data.get('ads_percentage_today', 0)
        draw.text((x, y + 90), f"Block Rate: {percent:.1f}%", font=fonts['20'], fill=0)
```

**Config:**
```yaml
- name: pihole
  type: pihole
  enabled: true
  position: [20, 340]
  size: [400, 120]
  update_interval: 60
  config:
    url: "http://pi.hole"
    api_token: "your_token_optional"
```

---

## 2. Docker Container Status

```python
"""Docker widget"""
import requests
from .base_widget import BaseWidget, WidgetRegistry

@WidgetRegistry.register('docker')
class DockerWidget(BaseWidget):
    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.socket_path = config['config'].get('socket', '/var/run/docker.sock')
        self.containers = config['config'].get('containers', [])

    def fetch_data(self):
        try:
            import docker
            client = docker.from_env()
            container_stats = []

            for container_name in self.containers:
                try:
                    container = client.containers.get(container_name)
                    container_stats.append({
                        'name': container_name,
                        'status': container.status,
                        'state': container.attrs['State']['Status']
                    })
                except:
                    container_stats.append({'name': container_name, 'status': 'not found'})

            return {'containers': container_stats}
        except Exception as e:
            self.logger.error(f"Failed to fetch Docker data: {e}")
            return None

    def render(self, draw, fonts, icon_loader):
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        draw.text((x, y), "DOCKER", font=fonts['28'], fill=0)

        y_offset = y + 40
        for container in data.get('containers', []):
            status = container['status']
            color = 0 if status == 'running' else 128
            draw.text((x, y_offset), f"{container['name']}: {status}", font=fonts['20'], fill=color)
            y_offset += 25
```

**Config:**
```yaml
- name: docker
  type: docker
  enabled: true
  position: [450, 340]
  size: [400, 120]
  update_interval: 30
  config:
    containers:
      - homeassistant
      - unifi-controller
      - pihole
```

**Requires:** `pip3 install docker`

---

## 3. Plex Media Server

```python
"""Plex widget"""
from plexapi.server import PlexServer
from .base_widget import BaseWidget, WidgetRegistry

@WidgetRegistry.register('plex')
class PlexWidget(BaseWidget):
    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.url = config['config']['url']
        self.token = config['config']['token']

    def fetch_data(self):
        try:
            plex = PlexServer(self.url, self.token)
            sessions = plex.sessions()

            streams = []
            for session in sessions:
                streams.append({
                    'user': session.usernames[0] if session.usernames else 'Unknown',
                    'title': session.title,
                    'type': session.type
                })

            return {
                'active_streams': len(streams),
                'streams': streams,
                'library_size': len(plex.library.all())
            }
        except Exception as e:
            self.logger.error(f"Failed to fetch Plex data: {e}")
            return None

    def render(self, draw, fonts, icon_loader):
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        draw.text((x, y), "PLEX", font=fonts['28'], fill=0)
        draw.text((x, y + 40), f"Active Streams: {data['active_streams']}", font=fonts['24'], fill=0)

        if data['active_streams'] > 0:
            y_offset = y + 70
            for stream in data['streams'][:2]:  # Show max 2
                draw.text((x, y_offset), f"{stream['user']}: {stream['title'][:20]}", font=fonts['20'], fill=0)
                y_offset += 25
```

**Config:**
```yaml
- name: plex
  type: plex
  enabled: true
  position: [900, 340]
  size: [400, 120]
  update_interval: 60
  config:
    url: "http://plex.local:32400"
    token: "YOUR_PLEX_TOKEN"
```

**Requires:** `pip3 install plexapi`

---

## 4. Tesla Vehicle Status

```python
"""Tesla widget"""
import requests
from .base_widget import BaseWidget, WidgetRegistry

@WidgetRegistry.register('tesla')
class TeslaWidget(BaseWidget):
    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.access_token = config['config']['access_token']
        self.vehicle_id = config['config']['vehicle_id']

    def fetch_data(self):
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            url = f"https://owner-api.teslamotors.com/api/1/vehicles/{self.vehicle_id}/vehicle_data"
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()['response']

            return {
                'battery_level': data['charge_state']['battery_level'],
                'battery_range': data['charge_state']['battery_range'],
                'charging_state': data['charge_state']['charging_state'],
                'locked': data['vehicle_state']['locked'],
                'odometer': data['vehicle_state']['odometer']
            }
        except Exception as e:
            self.logger.error(f"Failed to fetch Tesla data: {e}")
            return None

    def render(self, draw, fonts, icon_loader):
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        draw.text((x, y), "TESLA", font=fonts['28'], fill=0)

        battery = data['battery_level']
        draw.text((x, y + 40), f"Battery: {battery}%", font=fonts['24'], fill=0)
        draw.text((x, y + 70), f"Range: {data['battery_range']:.0f} mi", font=fonts['20'], fill=0)
        draw.text((x, y + 95), f"Status: {data['charging_state']}", font=fonts['20'], fill=0)
```

---

## 5. Synology NAS

```python
"""Synology NAS widget"""
import requests
from .base_widget import BaseWidget, WidgetRegistry

@WidgetRegistry.register('synology')
class SynologyWidget(BaseWidget):
    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.url = config['config']['url']
        self.username = config['config']['username']
        self.password = config['config']['password']
        self.session_id = None

    def login(self):
        try:
            url = f"{self.url}/webapi/auth.cgi"
            params = {
                'api': 'SYNO.API.Auth',
                'version': '3',
                'method': 'login',
                'account': self.username,
                'passwd': self.password,
                'session': 'FileStation',
                'format': 'sid'
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data['success']:
                self.session_id = data['data']['sid']
                return True
        except Exception as e:
            self.logger.error(f"Synology login failed: {e}")
        return False

    def fetch_data(self):
        if not self.session_id:
            if not self.login():
                return None

        try:
            # Get storage info
            url = f"{self.url}/webapi/entry.cgi"
            params = {
                'api': 'SYNO.Storage.CGI.Storage',
                'version': '1',
                'method': 'load_info',
                '_sid': self.session_id
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data['success']:
                volumes = data['data']['volumes']
                return {
                    'total_space': volumes[0]['size_total_byte'] / (1024**3),
                    'used_space': volumes[0]['size_used_byte'] / (1024**3),
                    'percent_used': (volumes[0]['size_used_byte'] / volumes[0]['size_total_byte']) * 100
                }
        except Exception as e:
            self.logger.error(f"Failed to fetch Synology data: {e}")
            self.session_id = None
        return None

    def render(self, draw, fonts, icon_loader):
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        draw.text((x, y), "NAS", font=fonts['28'], fill=0)
        draw.text((x, y + 40), f"Used: {data['used_space']:.1f} GB", font=fonts['20'], fill=0)
        draw.text((x, y + 65), f"Total: {data['total_space']:.1f} GB", font=fonts['20'], fill=0)
        draw.text((x, y + 90), f"{data['percent_used']:.1f}% Full", font=fonts['24'], fill=0)
```

---

## 6. MQTT Generic Widget

```python
"""MQTT widget for generic sensors"""
import json
import asyncio
from aiomqtt import Client
from .base_widget import BaseWidget, WidgetRegistry

@WidgetRegistry.register('mqtt')
class MQTTWidget(BaseWidget):
    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.broker = config['config']['broker']
        self.port = config['config'].get('port', 1883)
        self.topics = config['config']['topics']
        self.values = {}

    def fetch_data(self):
        try:
            async def get_messages():
                async with Client(self.broker, self.port) as client:
                    for topic_config in self.topics:
                        topic = topic_config['topic']
                        await client.subscribe(topic)

                    # Listen for a short time
                    async with asyncio.timeout(5):
                        async for message in client.messages:
                            payload = message.payload.decode()
                            self.values[str(message.topic)] = payload

            asyncio.run(get_messages())
            return {'topics': self.values}
        except Exception as e:
            self.logger.error(f"Failed to fetch MQTT data: {e}")
            return None

    def render(self, draw, fonts, icon_loader):
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        draw.text((x, y), "MQTT SENSORS", font=fonts['28'], fill=0)

        y_offset = y + 40
        for topic_config in self.topics:
            topic = topic_config['topic']
            display_name = topic_config.get('name', topic)
            value = data['topics'].get(topic, 'N/A')
            draw.text((x, y_offset), f"{display_name}: {value}", font=fonts['20'], fill=0)
            y_offset += 25
```

**Config:**
```yaml
- name: mqtt
  type: mqtt
  enabled: true
  position: [20, 240]
  size: [400, 100]
  update_interval: 30
  config:
    broker: "192.168.1.100"
    port: 1883
    topics:
      - topic: "home/temperature"
        name: "Temperature"
      - topic: "home/humidity"
        name: "Humidity"
```

---

## Icon Names You Might Need

Create these as 40x40 or 60x60 BMP files in the `icons/` directory:

- `icon_home.bmp` - Home/House
- `icon_temp.bmp` - Thermometer
- `icon_bulb.bmp` - Light bulb
- `icon_energy.bmp` - Lightning bolt
- `icon_network.bmp` - Network/ethernet
- `icon_server.bmp` - Server rack
- `icon_storage.bmp` - Hard drive
- `icon_docker.bmp` - Docker whale
- `icon_play.bmp` - Media play button
- `icon_car.bmp` - Vehicle
- `icon_lock.bmp` - Lock/security

You can use any BMP editor or convert from PNG/SVG.

---

## Quick Testing

Test your widget without the display:

```python
# test_widget.py
import sys
sys.path.append('.')

from PIL import Image, ImageDraw, ImageFont
from widgets.homeassistant_widget import HomeAssistantWidget

# Mock config
config = {
    'enabled': True,
    'position': [0, 0],
    'size': [400, 200],
    'update_interval': 60,
    'config': {
        'url': 'http://homeassistant.local:8123',
        'token': 'YOUR_TOKEN',
        'entities': [...]
    }
}

widget = HomeAssistantWidget(config, (0, 0), (400, 200))
data = widget.fetch_data()
print("Fetched data:", data)
```

---

## Home Assistant Advanced Examples

### Energy Dashboard

```yaml
- name: energy_dashboard
  type: homeassistant
  enabled: true
  position: [20, 20]
  size: [420, 200]
  config:
    url: "http://homeassistant.local:8123"
    token: "YOUR_TOKEN"
    entities:
      - entity_id: "sensor.total_power"
        display_name: "Current Power"
        unit: "W"
      - entity_id: "sensor.daily_energy"
        display_name: "Today"
        unit: "kWh"
      - entity_id: "sensor.solar_production"
        display_name: "Solar"
        unit: "W"
      - entity_id: "sensor.grid_import"
        display_name: "From Grid"
        unit: "W"
```

### Climate Control

```yaml
- name: climate
  type: homeassistant
  enabled: true
  position: [450, 20]
  size: [420, 150]
  config:
    url: "http://homeassistant.local:8123"
    token: "YOUR_TOKEN"
    entities:
      - entity_id: "climate.living_room"
        display_name: "Living Room"
      - entity_id: "sensor.living_room_temperature"
        display_name: "Current Temp"
      - entity_id: "sensor.living_room_humidity"
        display_name: "Humidity"
```

---

## Tips

1. **Stagger Updates**: Set different `initial_delay` values to avoid API rate limits
2. **Error Handling**: Always return `None` from `fetch_data()` on error
3. **Caching**: Use widget's `self.data` for last known good state
4. **Icons**: Keep icons simple - e-ink is black and white only
5. **Testing**: Use `dashboard_preview.png` output when testing without hardware

---

Happy widget building!
