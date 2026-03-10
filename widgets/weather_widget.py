"""Weather widget using Open-Meteo API"""
import requests
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .base_widget import BaseWidget, WidgetRegistry


@WidgetRegistry.register('weather')
class WeatherWidget(BaseWidget):
    """
    Display weather information from Open-Meteo with multi-day forecast

    Config options:
        api_url: Weather API endpoint
        show_forecast: Show daily forecast (default: true)
        show_aqi: Show air quality index (default: false)
    """

    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        # Get location from widget config or use default
        self.latitude = config['config'].get('latitude', 44.8240855)
        self.longitude = config['config'].get('longitude', 20.3834273)

        self.api_url = config['config'].get('api_url', 'https://api.open-meteo.com/v1/forecast')
        self.show_forecast = config['config'].get('show_forecast', True)

        # Cache für Standortdaten
        self.location_cache = None

    def fetch_location_name(self):
        """Hole Standortname via Reverse Geocoding"""
        if self.location_cache:
            return self.location_cache

        try:
            # Nominatim Reverse Geocoding
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': self.latitude,
                'lon': self.longitude,
                'format': 'json',
                'zoom': 10,
                'addressdetails': 1
            }
            headers = {'User-Agent': 'ePaperDashboard/1.0'}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            address = data.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village') or 'Unknown'
            state = address.get('state', '')

            self.location_cache = {'city': city, 'state': state}
            return self.location_cache

        except Exception as e:
            self.logger.warning(f"Could not fetch location name: {e}")
            return {'city': 'Unknown', 'state': ''}

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch weather data from Open-Meteo API"""
        try:
            # Fetch main weather data with daily forecast
            params = {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,'
                           'wind_direction_10m,surface_pressure,is_day,uv_index',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min',
                'timezone': 'auto',
                'forecast_days': 5
            }
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()
            weather_data = response.json()

            result = {
                'current': weather_data.get('current', {}),
                'daily': weather_data.get('daily', {}),
                'timezone': weather_data.get('timezone', 'UTC'),
            }

            # Hole Standortname
            location = self.fetch_location_name()
            result['location'] = location

            return result

        except Exception as e:
            self.logger.error(f"Failed to fetch weather data: {e}")
            return None

    def get_weather_icon(self, code, is_day=1):
        """Map weather code to icon name"""
        if code == 0:
            return "icon_sun" if is_day else "icon_moon"
        elif code in [1, 2]:
            return "icon_partly-cloudy-day"
        elif code == 3:
            return "icon_clouds"
        elif code in [45, 48]:
            return "icon_wind"
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            return "icon_rain"
        elif code in [71, 73, 75, 85, 86]:
            return "icon_snow"
        elif code in [95, 96, 99]:
            return "icon_lightning"
        return "icon_sun"

    def get_weekday_name(self, date_str):
        """Konvertiere Datum zu Wochentag (Deutsch)"""
        try:
            date_obj = datetime.fromisoformat(date_str)
            weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
            return weekdays[date_obj.weekday()]
        except:
            return ''

    def get_month_name(self, month_num):
        """Konvertiere Monatsnummer zu Name (Deutsch)"""
        months = ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
        return months[month_num] if 1 <= month_num <= 12 else ''

    def render(self, draw, fonts, icon_loader):
        """Render weather widget on the display"""
        data = self.get_data()
        if not data or 'current' not in data:
            self.draw_loading(draw)
            return

        x, y = self.position
        width, height = self.size

        current = data['current']
        temp = current.get('temperature_2m', 0)
        humidity = current.get('relative_humidity_2m', 0)
        pressure = current.get('surface_pressure', 0)
        weather_code = current.get('weather_code', 0)
        wind_speed = current.get('wind_speed_10m', 0)
        is_day = current.get('is_day', 1)
        uv_index = current.get('uv_index', 0.0)

        temp_rounded = math.floor(temp + 0.5)

        # Header: Standort
        location = data.get('location', {})
        city = location.get('city', 'Unknown')
        state = location.get('state', '')

        location_text = f"{city}, {state}" if state else city
        draw.text((x, y), location_text, font=fonts['28'], fill=0)

        # Datum: "Dienstag, 10 Juni 2026"
        now = datetime.now()
        weekday = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'][now.weekday()]
        month_name = self.get_month_name(now.month)
        date_text = f"{weekday}, {now.day} {month_name} {now.year}"
        draw.text((x, y + 35), date_text, font=fonts['24'], fill=0)

        # Divider
        draw.line((x, y + 68, x + width - 20, y + 68), fill=0, width=2)

        y_current = y + 80

        # Main temperature and weather icon
        icon_name = self.get_weather_icon(weather_code, is_day)
        icon = icon_loader(icon_name, (90, 90))
        if icon:
            draw.bitmap((x, y_current), icon, fill=0)

        draw.text((x + 100, y_current), f"{temp_rounded}°C", font=fonts['80'], fill=0)

        # UV Index (inverted if high)
        uv_x, uv_y = x + 320, y_current + 15
        uv_rounded = math.floor(uv_index + 0.5)
        draw.text((uv_x, uv_y), "UV", font=fonts['28'], fill=0)

        uv_val_str = str(uv_rounded)
        try:
            bbox = draw.textbbox((0, 0), uv_val_str, font=fonts['60'])
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            tw, th = draw.textsize(uv_val_str, font=fonts['60'])

        uv_val_x, uv_val_y = uv_x + 45, uv_y - 10
        if uv_rounded >= 6:
            # High UV - inverted display
            pad = 5
            draw.rectangle((uv_val_x - pad, uv_val_y - pad + 10,
                           uv_val_x + tw + pad, uv_val_y + th + pad), fill=0)
            draw.text((uv_val_x, uv_val_y), uv_val_str, font=fonts['60'], fill=255)
        else:
            draw.text((uv_val_x, uv_val_y), uv_val_str, font=fonts['60'], fill=0)

        # Additional info
        draw.text((x + 100, y_current + 85), f"Humidity: {humidity}%", font=fonts['20'], fill=0)
        draw.text((x + 100, y_current + 110), f"Wind: {wind_speed} km/h", font=fonts['20'], fill=0)

        # Divider
        draw.line((x, y_current + 140, x + width - 20, y_current + 140), fill=0, width=2)

        # Daily Forecast (nächste 4 Tage)
        if self.show_forecast and 'daily' in data:
            daily = data['daily']
            dates = daily.get('time', [])
            weather_codes = daily.get('weather_code', [])
            temp_max = daily.get('temperature_2m_max', [])
            temp_min = daily.get('temperature_2m_min', [])

            y_forecast = y_current + 155
            draw.text((x, y_forecast), "FORECAST", font=fonts['20'], fill=0)
            y_forecast += 30

            # Zeige nächste 4 Tage (skip heute)
            forecast_days = min(4, len(dates) - 1)
            day_width = width // forecast_days

            for i in range(1, forecast_days + 1):
                if i >= len(dates):
                    break

                day_x = x + (i - 1) * day_width

                # Wochentag
                weekday_short = self.get_weekday_name(dates[i])[:2]  # "Mo", "Di", etc.
                try:
                    bbox = draw.textbbox((0, 0), weekday_short, font=fonts['20'])
                    text_w = bbox[2] - bbox[0]
                except AttributeError:
                    text_w = draw.textsize(weekday_short, font=fonts['20'])[0]

                day_center_x = day_x + day_width // 2
                draw.text((day_center_x - text_w // 2, y_forecast), weekday_short, font=fonts['20'], fill=0)

                # Weather Icon
                icon_name = self.get_weather_icon(weather_codes[i], 1)
                icon = icon_loader(icon_name, (50, 50))
                if icon:
                    icon_x = day_center_x - 25
                    draw.bitmap((icon_x, y_forecast + 30), icon, fill=0)

                # Temperature (Max/Min)
                t_max = math.floor(temp_max[i] + 0.5)
                t_min = math.floor(temp_min[i] + 0.5)
                temp_text = f"{t_max}°/{t_min}°"

                try:
                    bbox = draw.textbbox((0, 0), temp_text, font=fonts['20'])
                    text_w = bbox[2] - bbox[0]
                except AttributeError:
                    text_w = draw.textsize(temp_text, font=fonts['20'])[0]

                draw.text((day_center_x - text_w // 2, y_forecast + 90), temp_text, font=fonts['20'], fill=0)
