#!/usr/bin/env python3
"""
Web-based configuration interface for ePaper Dashboard
"""
import os
import sys
import yaml
import subprocess
import glob
import importlib.util
from flask import Flask, render_template, jsonify, request
from pathlib import Path

app = Flask(__name__)

# Paths
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'config.yaml'
WIDGETS_DIR = BASE_DIR / 'widgets'

def load_config():
    """Load current configuration"""
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

def discover_widgets():
    """Discover all available widget types"""
    widgets = []

    # Scan all Python files in widgets directory
    for widget_file in glob.glob(str(WIDGETS_DIR / '*_widget.py')):
        if widget_file.endswith('base_widget.py'):
            continue

        # Extract widget type from filename
        widget_name = Path(widget_file).stem.replace('_widget', '')

        # Try to load the widget class to get its docstring
        try:
            spec = importlib.util.spec_from_file_location(widget_name, widget_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find the widget class
            widget_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    attr_name.endswith('Widget') and
                    attr_name != 'BaseWidget'):
                    widget_class = attr
                    break

            description = ''
            config_options = {}

            if widget_class and widget_class.__doc__:
                doc_lines = widget_class.__doc__.strip().split('\n')
                description = doc_lines[0] if doc_lines else ''

                # Try to extract config options from docstring
                in_config_section = False
                for line in doc_lines:
                    line = line.strip()
                    if 'Config options:' in line or 'Config Optionen:' in line:
                        in_config_section = True
                        continue
                    if in_config_section and ':' in line and not line.startswith('"""'):
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            desc = parts[1].strip()
                            config_options[key] = desc

            widgets.append({
                'type': widget_name,
                'name': widget_name.replace('_', ' ').title(),
                'description': description,
                'config_options': config_options,
                'file': widget_file
            })

        except Exception as e:
            print(f"Warning: Could not load widget {widget_name}: {e}")
            widgets.append({
                'type': widget_name,
                'name': widget_name.replace('_', ' ').title(),
                'description': 'Widget found but could not load details',
                'config_options': {},
                'file': widget_file
            })

    return sorted(widgets, key=lambda x: x['name'])

@app.route('/')
def index():
    """Main configuration page"""
    return render_template('config_ui.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        config = load_config()
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['POST'])
def save_config_endpoint():
    """Save configuration"""
    try:
        config = request.json
        save_config(config)
        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/widgets', methods=['GET'])
def get_available_widgets():
    """Get list of available widget types"""
    try:
        widgets = discover_widgets()
        return jsonify({
            'success': True,
            'widgets': widgets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/restart', methods=['POST'])
def restart_dashboard():
    """Restart the dashboard"""
    try:
        # Kill existing dashboard
        subprocess.run(['pkill', '-f', 'python3 main.py'], check=False)

        # Wait a moment
        import time
        time.sleep(1)

        # Clear cache
        subprocess.run(['find', '.', '-type', 'd', '-name', '__pycache__', '-exec', 'rm', '-rf', '{}', '+'],
                      cwd=BASE_DIR, check=False, stderr=subprocess.DEVNULL)
        subprocess.run(['find', '.', '-name', '*.pyc', '-delete'],
                      cwd=BASE_DIR, check=False, stderr=subprocess.DEVNULL)

        # Restart in background
        subprocess.Popen(['./run_dashboard.sh'],
                        cwd=BASE_DIR,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)

        return jsonify({
            'success': True,
            'message': 'Dashboard restart initiated'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/preview')
def get_preview():
    """Get current dashboard preview image"""
    preview_path = BASE_DIR / 'emulator_output' / 'preview.png'
    if preview_path.exists():
        from flask import send_file
        return send_file(preview_path, mimetype='image/png')
    else:
        return jsonify({
            'success': False,
            'error': 'Preview not available yet'
        }), 404

if __name__ == '__main__':
    print("=" * 60)
    print("ePaper Dashboard Configuration Interface")
    print("=" * 60)
    print("")
    print("Open your browser and go to:")
    print("  http://localhost:8080")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=8080)
