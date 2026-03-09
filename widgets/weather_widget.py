"""Weather widget using Open-Meteo API"""
import requests
import math
from typing import Dict, Any, Optional
from .base_widget import BaseWidget, WidgetRegistry


@WidgetRegistry.register('weather')
class WeatherWidget(BaseWidget):
    """
    Display weather information from Open-Meteo

    Config options:
        api_url: Weather API endpoint
        aqi_url: Air quality API endpoint
        show_forecast: Show 4-hour forecast (default: true)
        show_aqi: Show air quality index (default: true)
    """

    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        # Get location from widget config or use default
        self.latitude = config['config'].get('latitude', 44.8240855)
        self.longitude = config['config'].get('longitude', 20.3834273)

        self.api_url = config['config'].get('api_url', 'https://api.open-meteo.com/v1/forecast')
        self.aqi_url = config['config'].get('aqi_url', 'https://air-quality-api.open-meteo.com/v1/air-quality')
        self.show_forecast = config['config'].get('show_forecast', True)
        self.show_aqi = config['config'].get('show_aqi', True)

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch weather data from Open-Meteo API"""
        try:
            # Fetch main weather data
            params = {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,'
                           'wind_direction_10m,surface_pressure,is_day,uv_index',
                'hourly': 'temperature_2m,weather_code',
                'timezone': 'auto',
            }
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()
            weather_data = response.json()

            result = {
                'current': weather_data.get('current', {}),
                'hourly': weather_data.get('hourly', {}),
            }

            # Fetch AQI data if enabled
            if self.show_aqi:
                aqi_params = {
                    'latitude': self.latitude,
                    'longitude': self.longitude,
                    'current': 'european_aqi',
                }
                aqi_response = requests.get(self.aqi_url, params=aqi_params, timeout=10)
                aqi_response.raise_for_status()
                aqi_data = aqi_response.json()
                result['aqi'] = aqi_data.get('current', {}).get('european_aqi', 0)

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
        wind_dir = current.get('wind_direction_10m', 0)
        wind_speed = current.get('wind_speed_10m', 0)
        is_day = current.get('is_day', 1)
        uv_index = current.get('uv_index', 0.0)

        temp_rounded = math.floor(temp + 0.5)

        # Main temperature and weather icon
        icon_name = self.get_weather_icon(weather_code, is_day)
        icon = icon_loader(icon_name, (90, 90))
        if icon:
            draw.bitmap((x, y), icon, fill=0)

        draw.text((x + 100, y), f"{temp_rounded}°C", font=fonts['80'], fill=0)

        # UV Index (inverted if high)
        uv_x, uv_y = x + 320, y + 15
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
        draw.text((x + 100, y + 85), f"Humidity: {humidity}%", font=fonts['20'], fill=0)
        draw.text((x + 100, y + 110), f"Press: {pressure} hPa", font=fonts['20'], fill=0)

        # Divider
        draw.line((x, y + 135, x + width - 20, y + 135), fill=0, width=2)

        # Wind compass
        y_compass = y + 155
        icon_wind = icon_loader("icon_wind", (30, 30))
        if icon_wind:
            draw.bitmap((x + 5, y_compass), icon_wind, fill=0)

        # Draw compass
        cx, cy, r = x + 80, y_compass + 70, 55
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=0, width=2)

        # Compass ticks and labels
        for angle in range(0, 360, 45):
            rad_tick = math.radians(angle)
            inner_r = r - 8 if angle % 90 == 0 else r - 4
            tx1, ty1 = cx + inner_r * math.cos(rad_tick), cy + inner_r * math.sin(rad_tick)
            tx2, ty2 = cx + r * math.cos(rad_tick), cy + r * math.sin(rad_tick)
            draw.line((tx1, ty1, tx2, ty2), fill=0, width=2)

        draw.text((cx - 8, cy - r - 22), "N", font=fonts['20'], fill=0)
        draw.text((cx - 8, cy + r + 4), "S", font=fonts['20'], fill=0)
        draw.text((cx + r + 6, cy - 10), "E", font=fonts['20'], fill=0)
        draw.text((cx - r - 24, cy - 10), "W", font=fonts['20'], fill=0)

        # Wind direction arrow
        rad_arrow = math.radians(wind_dir - 90)
        tip_x = cx + (r - 12) * math.cos(rad_arrow)
        tip_y = cy + (r - 12) * math.sin(rad_arrow)
        base_angle = math.radians(150)
        left_x = cx + 20 * math.cos(rad_arrow + base_angle)
        left_y = cy + 20 * math.sin(rad_arrow + base_angle)
        right_x = cx + 20 * math.cos(rad_arrow - base_angle)
        right_y = cy + 20 * math.sin(rad_arrow - base_angle)
        draw.polygon([(tip_x, tip_y), (left_x, left_y), (right_x, right_y)], fill=0)
        draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=0)

        # Wind speed
        spd_text = f"{wind_speed} km/h"
        try:
            bbox = draw.textbbox((0, 0), spd_text, font=fonts['20'])
            tw = bbox[2] - bbox[0]
        except AttributeError:
            tw = draw.textsize(spd_text, font=fonts['20'])[0]
        draw.text((cx - tw / 2, cy + 25), spd_text, font=fonts['20'], fill=0)

        # AQI if enabled
        if self.show_aqi and 'aqi' in data:
            aqi = data['aqi']
            aqi_x = x + 180
            draw.text((aqi_x, y_compass), "AIR QUALITY", font=fonts['20'], fill=0)
            draw.text((aqi_x, y_compass + 45), "AQI:", font=fonts['28'], fill=0)

            aqi_str = str(int(aqi))
            try:
                bbox = draw.textbbox((0, 0), aqi_str, font=fonts['80'])
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            except AttributeError:
                tw, th = draw.textsize(aqi_str, font=fonts['80'])

            val_x, val_y = aqi_x + 80, y_compass + 56

            if aqi >= 50:
                # Poor air quality - inverted display
                pad = 20
                draw.rectangle((val_x - pad, val_y - pad + 15,
                               val_x + tw + pad, val_y + th + pad - 5), fill=0)
                draw.text((val_x, val_y), aqi_str, font=fonts['80'], fill=255)
            else:
                draw.text((val_x, val_y), aqi_str, font=fonts['80'], fill=0)
