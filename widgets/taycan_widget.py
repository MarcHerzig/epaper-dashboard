"""Porsche Taycan Widget für ePaper Dashboard"""
import requests
from io import BytesIO
from PIL import Image
from typing import Dict, Any, Optional
from .base_widget import BaseWidget, WidgetRegistry


@WidgetRegistry.register('taycan')
class TaycanWidget(BaseWidget):
    """
    Zeigt Porsche Taycan Status über Home Assistant

    Config Optionen:
        url: Home Assistant URL
        token: Long-lived access token
        battery_entity: Entity ID für Batteriestand
        range_entity: Entity ID für Reichweite
        charging_entity: Entity ID für Ladestatus
        image_url: URL zum Taycan Bild (optional)
        image_entity: Entity ID mit Bild URL (optional)
    """

    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.base_url = config['config']['url'].rstrip('/')
        self.token = config['config']['token']

        # Entity IDs
        self.battery_entity = config['config'].get('battery_entity', 'sensor.taycan_battery_level')
        self.range_entity = config['config'].get('range_entity', 'sensor.taycan_range')
        self.charging_entity = config['config'].get('charging_entity', 'binary_sensor.taycan_charging')

        # Bild Konfiguration
        self.image_url = config['config'].get('image_url', None)
        self.image_entity = config['config'].get('image_entity', None)

        # HTTP Session
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        })

        # Cache für das Bild
        self.car_image = None

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Hole Taycan Daten von Home Assistant"""
        try:
            result = {
                'battery': 0,
                'range': 0,
                'charging': False,
                'image_available': False
            }

            # Batteriestand
            try:
                url = f"{self.base_url}/api/states/{self.battery_entity}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                result['battery'] = float(data.get('state', 0))
            except Exception as e:
                self.logger.error(f"Fehler beim Abrufen des Batteriestands: {e}")

            # Reichweite
            try:
                url = f"{self.base_url}/api/states/{self.range_entity}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                result['range'] = int(float(data.get('state', 0)))
                # Unit von HA übernehmen (falls vorhanden)
                result['range_unit'] = data.get('attributes', {}).get('unit_of_measurement', 'km')
            except Exception as e:
                self.logger.error(f"Fehler beim Abrufen der Reichweite: {e}")

            # Ladestatus
            try:
                url = f"{self.base_url}/api/states/{self.charging_entity}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                state = data.get('state', '').lower()
                result['charging_status'] = data.get('state', 'Unknown')
                # Verschiedene Ladestatus Texte erkennen
                result['charging'] = any(keyword in state for keyword in ['charging', 'lädt', 'laden', 'connected'])
            except Exception as e:
                self.logger.error(f"Fehler beim Abrufen des Ladestatus: {e}")

            # Bild laden (wenn noch nicht gecacht)
            if self.car_image is None:
                self._load_car_image()
            result['image_available'] = (self.car_image is not None)

            return result

        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Taycan Daten: {e}")
            return None

    def _load_car_image(self):
        """Lade das Taycan Bild"""
        try:
            # Bild URL aus Entity holen (wenn konfiguriert)
            if self.image_entity:
                # Für image.* Entities: Hole das Bild direkt über die entity_picture
                url = f"{self.base_url}/api/states/{self.image_entity}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

                # Hole entity_picture aus den Attributen (für image.* entities)
                entity_picture = data.get('attributes', {}).get('entity_picture')

                if entity_picture:
                    self.image_url = entity_picture
                else:
                    # Fallback: state als URL verwenden
                    state = data.get('state', '')
                    if state and (state.startswith('http') or state.startswith('/')):
                        self.image_url = state

            # Bild herunterladen
            if self.image_url:
                # Wenn URL relativ ist, HA Base URL hinzufügen
                if self.image_url.startswith('/'):
                    image_url = f"{self.base_url}{self.image_url}"
                else:
                    image_url = self.image_url

                self.logger.info(f"Lade Bild von: {image_url}")

                response = self.session.get(image_url, timeout=15)
                response.raise_for_status()

                # Bild laden und für E-Ink optimieren
                img = Image.open(BytesIO(response.content))

                # Konvertiere zu RGB falls nötig, dann zu Graustufen
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img = img.convert('L')

                # Resize mit LANCZOS für beste Qualität
                img = img.resize((500, 250), Image.Resampling.LANCZOS)

                # Optimierung für E-Ink Display
                from PIL import ImageEnhance, ImageFilter

                # Schärfen für bessere Details
                img = img.filter(ImageFilter.SHARPEN)

                # Kontrast erhöhen
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.4)

                # Helligkeit anpassen
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.05)

                # WICHTIG: Direkt zu 1-bit mit Floyd-Steinberg Dithering konvertieren
                # Das ist besser als es später beim paste zu machen
                self.car_image = img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)

                self.logger.info("Taycan Bild erfolgreich geladen")

        except Exception as e:
            self.logger.warning(f"Bild konnte nicht geladen werden: {e}")
            self.car_image = None

    def render(self, draw, fonts, icon_loader):
        """Render Taycan Widget auf dem Display"""
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        width, height = self.size

        # Header mit Icon
        icon = icon_loader("icon_car", (50, 50))
        if icon:
            draw.bitmap((x, y), icon, fill=0)

        draw.text((x + 60, y + 5), "PORSCHE TAYCAN", font=fonts['28'], fill=0)

        # Ladestatus Indikator - nur anzeigen wenn das Auto lädt
        if data.get('charging', False):
            charging_status = data.get('charging_status', '')
            draw.text((x + 60, y + 35), f"🔌 {charging_status}", font=fonts['20'], fill=0)
            y_offset = y + 50
        else:
            y_offset = y + 32

        # Auto Bild (wenn verfügbar)
        if data.get('image_available') and self.car_image:
            # Zentriere das Bild
            img_x = x + (width - 500) // 2
            draw.bitmap((img_x, y_offset), self.car_image, fill=0)
            y_offset += 260

        # Batteriestand und Reichweite nebeneinander
        battery = data.get('battery', 0)
        range_km = data.get('range', 0)
        range_unit = data.get('range_unit', 'km')

        # Berechne Positionen für zentrierte Anzeige
        section_width = width // 2

        # Batterie links
        battery_x = x + 20
        draw.text((battery_x, y_offset), "Batterie:", font=fonts['24'], fill=0)
        battery_text = f"{battery:.0f}%"
        draw.text((battery_x, y_offset + 30), battery_text, font=fonts['60'], fill=0)

        # Batterie Balken
        bar_width = 180
        bar_height = 20
        bar_y = y_offset + 100
        draw.rectangle((battery_x, bar_y, battery_x + bar_width, bar_y + bar_height), outline=0, width=2)
        fill_width = int((battery / 100) * (bar_width - 4))
        if fill_width > 0:
            draw.rectangle((battery_x + 2, bar_y + 2, battery_x + 2 + fill_width, bar_y + bar_height - 2), fill=0)

        # Reichweite rechts
        range_x = x + section_width + 20
        draw.text((range_x, y_offset), "Reichweite:", font=fonts['24'], fill=0)
        draw.text((range_x, y_offset + 30), f"{range_km} {range_unit}", font=fonts['60'], fill=0)
