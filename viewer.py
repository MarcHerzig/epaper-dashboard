#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Web-based Dashboard Viewer
View the emulated dashboard in your browser with auto-refresh
"""
import os
import sys
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading


class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving dashboard preview"""

    def __init__(self, *args, **kwargs):
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.output_dir = os.path.join(self.base_dir, 'emulator_output')
        super().__init__(*args, directory=self.base_dir, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            self.send_dashboard_html()
        elif self.path == '/preview.png':
            self.serve_preview_image()
        elif self.path == '/current.png':
            self.serve_current_image()
        elif self.path == '/status':
            self.send_status()
        else:
            super().do_GET()

    def send_dashboard_html(self):
        """Send the dashboard viewer HTML"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>ePaper Dashboard Viewer</title>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 20px;
        }

        h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .info {
            color: #888;
            font-size: 14px;
        }

        .display-container {
            background: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            max-width: 100%;
            overflow: auto;
        }

        .display-frame {
            border: 2px solid #333;
            background: #ffffff;
            position: relative;
        }

        #dashboard-image {
            display: block;
            width: 1360px;
            height: 480px;
            image-rendering: crisp-edges;
            image-rendering: pixelated;
        }

        .controls {
            margin-top: 20px;
            text-align: center;
        }

        .button {
            background: #0066cc;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin: 0 5px;
            transition: background 0.2s;
        }

        .button:hover {
            background: #0052a3;
        }

        .button:active {
            transform: translateY(1px);
        }

        .button.secondary {
            background: #444;
        }

        .button.secondary:hover {
            background: #555;
        }

        .status {
            margin-top: 20px;
            padding: 15px;
            background: #2a2a2a;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            text-align: left;
            max-width: 1400px;
            width: 100%;
        }

        .status-label {
            color: #888;
            display: inline-block;
            width: 150px;
        }

        .status-value {
            color: #0f0;
        }

        .auto-refresh {
            display: inline-block;
            margin-left: 10px;
            color: #0f0;
            font-size: 12px;
        }

        .auto-refresh.paused {
            color: #f90;
        }

        @media (max-width: 1440px) {
            #dashboard-image {
                width: 100%;
                height: auto;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📺 ePaper Dashboard Viewer</h1>
        <p class="info">Waveshare 10.85" Display Emulator (1360×480)</p>
        <span class="auto-refresh" id="refresh-status">● Auto-refresh: ON</span>
    </div>

    <div class="display-container">
        <div class="display-frame">
            <img id="dashboard-image" src="/preview.png" alt="Dashboard Preview">
        </div>
    </div>

    <div class="controls">
        <button class="button" onclick="refreshNow()">🔄 Refresh Now</button>
        <button class="button secondary" onclick="toggleAutoRefresh()">
            <span id="toggle-text">⏸ Pause Auto-Refresh</span>
        </button>
        <button class="button secondary" onclick="openInNewTab()">🔍 Open Full Size</button>
    </div>

    <div class="status">
        <div><span class="status-label">Last Update:</span><span class="status-value" id="last-update">Never</span></div>
        <div><span class="status-label">Auto-refresh:</span><span class="status-value" id="refresh-rate">Every 2 seconds</span></div>
        <div><span class="status-label">Frame Count:</span><span class="status-value" id="frame-count">-</span></div>
    </div>

    <script>
        let autoRefresh = true;
        let refreshInterval = null;
        let frameCount = 0;

        function refreshNow() {
            const img = document.getElementById('dashboard-image');
            // Add timestamp to prevent caching
            img.src = '/preview.png?t=' + new Date().getTime();
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            frameCount++;
            document.getElementById('frame-count').textContent = frameCount;
        }

        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            const status = document.getElementById('refresh-status');
            const toggleText = document.getElementById('toggle-text');

            if (autoRefresh) {
                status.textContent = '● Auto-refresh: ON';
                status.className = 'auto-refresh';
                toggleText.textContent = '⏸ Pause Auto-Refresh';
                startAutoRefresh();
            } else {
                status.textContent = '● Auto-refresh: PAUSED';
                status.className = 'auto-refresh paused';
                toggleText.textContent = '▶ Resume Auto-Refresh';
                stopAutoRefresh();
            }
        }

        function startAutoRefresh() {
            if (refreshInterval) return;
            refreshInterval = setInterval(refreshNow, 2000); // Every 2 seconds
        }

        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        }

        function openInNewTab() {
            window.open('/preview.png?t=' + new Date().getTime(), '_blank');
        }

        // Start auto-refresh on load
        window.addEventListener('load', () => {
            refreshNow();
            startAutoRefresh();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' || e.key === 'R') {
                refreshNow();
            } else if (e.key === ' ') {
                e.preventDefault();
                toggleAutoRefresh();
            }
        });
    </script>
</body>
</html>
        """

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', len(html.encode()))
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_preview_image(self):
        """Serve the preview image"""
        preview_path = os.path.join(self.output_dir, 'preview.png')
        if os.path.exists(preview_path):
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')

            with open(preview_path, 'rb') as f:
                image_data = f.read()
                self.send_header('Content-Length', len(image_data))
                self.end_headers()
                self.wfile.write(image_data)
        else:
            self.send_error(404, "Preview image not found")

    def serve_current_image(self):
        """Serve the current image"""
        current_path = os.path.join(self.output_dir, 'current.png')
        if os.path.exists(current_path):
            with open(current_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_error(404, "Current image not found")

    def send_status(self):
        """Send status information"""
        import json

        status = {
            'running': True,
            'timestamp': time.time(),
            'output_dir': self.output_dir
        }

        response = json.dumps(status).encode()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        """Suppress logging of requests"""
        # Only log errors
        if args[1] != '200':
            super().log_message(format, *args)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads"""
    daemon_threads = True


def run_viewer(port=8080):
    """Run the web viewer"""
    server_address = ('', port)
    httpd = ThreadedHTTPServer(server_address, DashboardHandler)

    print("=" * 60)
    print("ePaper Dashboard Web Viewer")
    print("=" * 60)
    print(f"\n✓ Server started on http://localhost:{port}")
    print(f"✓ Open in your browser: http://localhost:{port}")
    print("\nThe viewer will auto-refresh every 2 seconds")
    print("Run main_v2.py in another terminal to see live updates")
    print("\nKeyboard shortcuts:")
    print("  R - Refresh now")
    print("  Space - Pause/resume auto-refresh")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down viewer...")
        httpd.shutdown()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='View ePaper dashboard in browser')
    parser.add_argument('--port', type=int, default=8080, help='Port to run web server on (default: 8080)')
    args = parser.parse_args()

    run_viewer(args.port)
