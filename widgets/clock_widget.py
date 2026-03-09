"""Clock and date widget"""
from datetime import datetime
from typing import Dict, Any, Optional
from .base_widget import BaseWidget, WidgetRegistry


@WidgetRegistry.register('clock')
class ClockWidget(BaseWidget):
    """
    Display current time and date

    Config options:
        format: "12h" or "24h" (default: "24h")
        show_date: Show date (default: true)
        show_day: Show day of week (default: true)
    """

    def __init__(self, config, position, size):
        super().__init__(config, position, size)
        self.format = config['config'].get('format', '24h')
        self.show_date = config['config'].get('show_date', True)
        self.show_day = config['config'].get('show_day', True)

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Get current time and date"""
        now = datetime.now()

        if self.format == '12h':
            time_str = now.strftime('%I:%M')
            period = now.strftime('%p')
        else:
            time_str = now.strftime('%H:%M')
            period = None

        return {
            'time': time_str,
            'period': period,
            'date': now.strftime('%d. %b %Y'),
            'day': now.strftime('%A'),
            'timestamp': now.timestamp(),
        }

    def render(self, draw, fonts, icon_loader):
        """Render clock on the display"""
        data = self.get_data()
        if not data:
            self.draw_loading(draw)
            return

        x, y = self.position
        width, height = self.size

        # Time
        time_str = data['time']
        try:
            # Use special clock font if available
            time_font = fonts.get('clock', fonts['80'])
        except:
            time_font = fonts['80']

        # Center the time
        try:
            bbox = draw.textbbox((0, 0), time_str, font=time_font)
            time_width = bbox[2] - bbox[0]
        except AttributeError:
            time_width = draw.textsize(time_str, font=time_font)[0]

        time_x = x + (width - time_width) // 2
        draw.text((time_x, y), time_str, font=time_font, fill=0)

        y_offset = y + 140

        # AM/PM for 12-hour format
        if data.get('period'):
            period_x = x + width - 80
            draw.text((period_x, y + 20), data['period'], font=fonts['32'], fill=0)

        # Date
        if self.show_date:
            date_str = data['date']
            try:
                bbox = draw.textbbox((0, 0), date_str, font=fonts['28'])
                date_width = bbox[2] - bbox[0]
            except AttributeError:
                date_width = draw.textsize(date_str, font=fonts['28'])[0]

            date_x = x + (width - date_width) // 2
            draw.text((date_x, y_offset), date_str, font=fonts['28'], fill=0)
            y_offset += 35

        # Day of week
        if self.show_day:
            day_str = data['day']
            try:
                bbox = draw.textbbox((0, 0), day_str, font=fonts['24'])
                day_width = bbox[2] - bbox[0]
            except AttributeError:
                day_width = draw.textsize(day_str, font=fonts['24'])[0]

            day_x = x + (width - day_width) // 2
            draw.text((day_x, y_offset), day_str, font=fonts['24'], fill=0)
