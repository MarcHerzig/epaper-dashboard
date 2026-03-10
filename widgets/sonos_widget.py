"""Sonos widget for ePaper dashboard via Home Assistant"""
import requests
from io import BytesIO
from PIL import Image
from typing import Dict, Any, Optional
from .base_widget import BaseWidget, WidgetRegistry


@WidgetRegistry.register('sonos')
class SonosWidget(BaseWidget):
    """
    Display Sonos media player status via Home Assistant

    Config options:
        url: Home Assistant URL (e.g., "https://ha.example.com")
        token: Long-lived access token
        entity_id: Media player entity ID (e.g., "media_player.sonos_buro")
        show_album: Show album name (default: true)
        show_volume: Show volume level (default: false)
    """

    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.base_url = config['config']['url'].rstrip('/')
        self.token = config['config']['token']
        self.entity_id = config['config'].get('entity_id', 'media_player.sonos_buro')
        self.show_album = config['config'].get('show_album', True)
        self.show_volume = config['config'].get('show_volume', False)

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        })

        # Cache für Album Cover
        self.album_art_cache = {}
        self.last_album_art_url = None

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch Sonos media player state from Home Assistant"""
        try:
            url = f"{self.base_url}/api/states/{self.entity_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            state_data = response.json()

            state = state_data.get('state', 'unknown')
            attributes = state_data.get('attributes', {})

            # Album Art URL
            entity_picture = attributes.get('entity_picture', '')
            album_art_url = None
            if entity_picture:
                if entity_picture.startswith('/'):
                    album_art_url = f"{self.base_url}{entity_picture}"
                else:
                    album_art_url = entity_picture

            # Lade Album Art wenn URL sich geändert hat
            album_art_image = None
            if album_art_url and album_art_url != self.last_album_art_url:
                album_art_image = self._load_album_art(album_art_url)
                self.last_album_art_url = album_art_url

            return {
                'state': state,  # playing, paused, idle, off
                'media_title': attributes.get('media_title', ''),
                'media_artist': attributes.get('media_artist', ''),
                'media_album_name': attributes.get('media_album_name', ''),
                'volume_level': attributes.get('volume_level', 0),
                'source': attributes.get('source', ''),
                'friendly_name': attributes.get('friendly_name', 'Sonos'),
                'album_art_url': album_art_url,
                'album_art_image': album_art_image,
            }

        except Exception as e:
            self.logger.error(f"Failed to fetch Sonos data: {e}")
            return None

    def _load_album_art(self, url):
        """Lade Album Cover Bild"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Bild laden und für E-Ink optimieren
            img = Image.open(BytesIO(response.content))

            # Konvertiere zu Graustufen
            if img.mode != 'L':
                img = img.convert('L')

            # Resize auf kleine Größe für Album Cover
            img = img.resize((100, 100), Image.Resampling.LANCZOS)

            # Optimierung für E-Ink
            from PIL import ImageEnhance, ImageFilter
            img = img.filter(ImageFilter.SHARPEN)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)

            # Konvertiere zu 1-bit mit Dithering
            img_1bit = img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)

            self.logger.info(f"Album art loaded successfully")
            return img_1bit

        except Exception as e:
            self.logger.warning(f"Could not load album art: {e}")
            return None

    def render(self, draw, fonts, icon_loader):
        """Render Sonos widget on the display"""
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        width, height = self.size

        state = data.get('state', 'unknown')
        title = data.get('media_title', '')
        artist = data.get('media_artist', '')
        album = data.get('media_album_name', '')
        volume = data.get('volume_level', 0)
        speaker_name = data.get('friendly_name', 'Sonos')
        album_art = data.get('album_art_image')

        # Header with speaker name
        draw.text((x, y), speaker_name.upper(), font=fonts['24'], fill=0)

        y_offset = y + 35

        if state in ['playing', 'paused'] and (title or artist):
            # Layout: Album Cover links, Text rechts

            # Album Cover (wenn verfügbar)
            cover_x = x
            cover_size = 100

            if album_art:
                draw.bitmap((cover_x, y_offset), album_art, fill=0)
                text_x = cover_x + cover_size + 15
            else:
                # Kein Album Art - zeige Play/Pause Icon
                if state == 'playing':
                    icon = icon_loader("icon_play", (40, 40))
                elif state == 'paused':
                    icon = icon_loader("icon_pause", (40, 40))
                else:
                    icon = None

                if icon:
                    draw.bitmap((cover_x, y_offset), icon, fill=0)
                text_x = cover_x + 50

            # Text rechts vom Cover
            max_chars = 30
            line_height = 28

            # Artist (oben)
            if artist:
                artist_display = artist if len(artist) <= max_chars else artist[:max_chars-3] + "..."
                draw.text((text_x, y_offset), artist_display, font=fonts['24'], fill=0)

            # Song Title (darunter)
            if title:
                title_display = title if len(title) <= max_chars else title[:max_chars-3] + "..."
                draw.text((text_x, y_offset + line_height), title_display, font=fonts['20'], fill=0)

            # Album (optional, ganz unten)
            if self.show_album and album:
                album_display = album if len(album) <= max_chars else album[:max_chars-3] + "..."
                draw.text((text_x, y_offset + line_height * 2), album_display, font=fonts['20'], fill=0)

        elif state == 'idle':
            draw.text((x, y_offset), "Idle - Keine Wiedergabe", font=fonts['20'], fill=0)
        elif state == 'off':
            draw.text((x, y_offset), "Ausgeschaltet", font=fonts['20'], fill=0)
        else:
            draw.text((x, y_offset), "Keine Medien", font=fonts['20'], fill=0)

        # Volume (if enabled)
        if self.show_volume:
            volume_y = y + height - 25
            volume_pct = int(volume * 100)
            draw.text((x, volume_y), f"Lautstärke: {volume_pct}%", font=fonts['20'], fill=0)
