"""Ubiquiti UniFi widget for ePaper dashboard"""
import requests
import urllib3
from typing import Dict, Any, Optional
from .base_widget import BaseWidget, WidgetRegistry

# Disable SSL warnings if verify_ssl is False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@WidgetRegistry.register('ubiquiti')
class UbiquitiWidget(BaseWidget):
    """
    Display Ubiquiti UniFi network statistics

    Config options:
        controller_url: UniFi Controller URL (e.g., "https://unifi.local:8443")
        username: Controller username
        password: Controller password
        site: Site name (default: "default")
        verify_ssl: Verify SSL certificates (default: false)
        show: List of what to display ['wan_status', 'bandwidth', 'client_count', 'devices']
    """

    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.controller_url = config['config']['controller_url'].rstrip('/')
        self.username = config['config']['username']
        self.password = config['config']['password']
        self.site = config['config'].get('site', 'default')
        self.verify_ssl = config['config'].get('verify_ssl', False)
        self.show = config['config'].get('show', ['wan_status', 'bandwidth', 'client_count'])

        self.session = requests.Session()
        self.session.verify = self.verify_ssl
        self.logged_in = False

    def login(self) -> bool:
        """Login to UniFi Controller"""
        try:
            login_url = f"{self.controller_url}/api/login"
            payload = {
                'username': self.username,
                'password': self.password,
            }
            response = self.session.post(login_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logged_in = True
            self.logger.info("Successfully logged in to UniFi Controller")
            return True
        except Exception as e:
            self.logger.error(f"Failed to login to UniFi Controller: {e}")
            self.logged_in = False
            return False

    def logout(self):
        """Logout from UniFi Controller"""
        try:
            logout_url = f"{self.controller_url}/api/logout"
            self.session.post(logout_url, timeout=5)
        except:
            pass

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch network statistics from UniFi Controller"""
        if not self.logged_in:
            if not self.login():
                return None

        try:
            result = {}

            # Fetch health data (includes WAN status, uptime)
            if 'wan_status' in self.show:
                health_url = f"{self.controller_url}/api/s/{self.site}/stat/health"
                response = self.session.get(health_url, timeout=10)
                response.raise_for_status()
                health_data = response.json()

                if health_data.get('meta', {}).get('rc') == 'ok':
                    for item in health_data.get('data', []):
                        if item.get('subsystem') == 'wan':
                            result['wan'] = {
                                'status': item.get('status', 'unknown'),
                                'uptime': item.get('uptime', 0),
                                'ip': item.get('wan_ip', 'N/A'),
                                'latency': item.get('latency', 0),
                                'speedtest_ping': item.get('speedtest_ping', 0),
                            }

            # Fetch bandwidth statistics
            if 'bandwidth' in self.show:
                stats_url = f"{self.controller_url}/api/s/{self.site}/stat/health"
                response = self.session.get(stats_url, timeout=10)
                response.raise_for_status()
                stats_data = response.json()

                if stats_data.get('meta', {}).get('rc') == 'ok':
                    for item in stats_data.get('data', []):
                        if item.get('subsystem') == 'wan':
                            result['bandwidth'] = {
                                'tx_bytes': item.get('tx_bytes-r', 0),
                                'rx_bytes': item.get('rx_bytes-r', 0),
                            }

            # Fetch client count
            if 'client_count' in self.show:
                clients_url = f"{self.controller_url}/api/s/{self.site}/stat/sta"
                response = self.session.get(clients_url, timeout=10)
                response.raise_for_status()
                clients_data = response.json()

                if clients_data.get('meta', {}).get('rc') == 'ok':
                    clients = clients_data.get('data', [])
                    result['clients'] = {
                        'total': len(clients),
                        'wired': len([c for c in clients if not c.get('is_wired', True) == False]),
                        'wireless': len([c for c in clients if c.get('is_wired', False) == False]),
                    }

            return result

        except Exception as e:
            self.logger.error(f"Failed to fetch UniFi data: {e}")
            self.logged_in = False
            return None

    def render(self, draw, fonts, icon_loader):
        """Render Ubiquiti network stats on the display"""
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        width, height = self.size

        # Header
        icon = icon_loader("icon_wifi", (40, 40))
        if icon:
            draw.bitmap((x, y), icon, fill=0)
        draw.text((x + 50, y + 5), "NETWORK STATUS", font=fonts['28'], fill=0)

        y_offset = y + 50

        # WAN Status
        if 'wan' in data:
            wan = data['wan']
            status = wan['status']
            status_text = "UP" if status == 'ok' else "DOWN"
            color = 0 if status == 'ok' else 255

            draw.text((x, y_offset), "WAN:", font=fonts['24'], fill=0)
            draw.text((x + 80, y_offset), status_text, font=fonts['24'], fill=color)

            # Uptime
            uptime_hours = wan['uptime'] // 3600
            draw.text((x + 200, y_offset), f"Up: {uptime_hours}h", font=fonts['20'], fill=0)

            y_offset += 30

        # Bandwidth
        if 'bandwidth' in data:
            bw = data['bandwidth']
            # Convert bytes/s to Mbps
            tx_mbps = (bw['tx_bytes'] * 8) / 1_000_000
            rx_mbps = (bw['rx_bytes'] * 8) / 1_000_000

            # Upload
            draw.text((x, y_offset), f"↑ {tx_mbps:.2f} Mbps", font=fonts['20'], fill=0)

            # Download
            draw.text((x + 200, y_offset), f"↓ {rx_mbps:.2f} Mbps", font=fonts['20'], fill=0)

            y_offset += 30

        # Client Count
        if 'clients' in data:
            clients = data['clients']
            total = clients['total']
            wireless = clients.get('wireless', 0)
            wired = clients.get('wired', 0)

            draw.text((x, y_offset), f"Clients: {total}", font=fonts['20'], fill=0)
            draw.text((x + 150, y_offset), f"WiFi: {wireless} | Wired: {wired}", font=fonts['20'], fill=0)
