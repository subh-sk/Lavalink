import json
import logging
import os
import socket
import uuid

import requests
import websocket
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lavalink_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration constants
CONFIG_FILE = 'lavalink_configs.json'
DEFAULT_CONFIG = {
    'host': 'lavalink',
    'port': 2333,
    'password': 'admin123',
    'secure': False
}

class ConfigManager:
    @staticmethod
    def load_configs():
        """Load Lavalink configurations from file."""
        try:
            if not os.path.exists(CONFIG_FILE):
                return {}
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading configs: {e}")
            return {}

    @staticmethod
    def save_configs(configs):
        """Save Lavalink configurations to file."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(configs, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving configs: {e}")

class LavalinkConnectionManager:
    @staticmethod
    def test_connection(config):
        """
        Test Lavalink connection with comprehensive checks
        
        Args:
            config (dict): Connection configuration
        
        Returns:
            dict: Connection test results
        """
        try:
            # Validate input
            if not all(key in config for key in ['host', 'port', 'password']):
                return {
                    'success': False,
                    'message': 'Invalid connection details',
                    'details': config
                }

            # Socket connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((config['host'], config['port']))
            sock.close()

            if result != 0:
                return {
                    'success': False,
                    'message': 'Socket connection failed',
                    'details': config
                }

            # WebSocket connection test
            ws_url = f"ws://{config['host']}:{config['port']}/websocket"
            ws = websocket.create_connection(
                ws_url, 
                header={"Authorization": config['password']},
                timeout=5
            )
            ws.close()

            return {
                'success': True,
                'message': 'Connection successful',
                'details': config
            }

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                'success': False,
                'message': str(e),
                'details': config
            }

# Flask Application Setup
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/lavalink/connection', methods=['GET'])
def get_lavalink_connection():
    """Get default Lavalink connection details."""
    return jsonify(DEFAULT_CONFIG)

@app.route('/api/lavalink/configs', methods=['GET', 'POST'])
def manage_lavalink_configs():
    """Manage Lavalink connection configurations."""
    if request.method == 'GET':
        configs = ConfigManager.load_configs()
        return jsonify(configs)
    
    config = request.json
    config_id = config.get('id', str(uuid.uuid4()))
    config['id'] = config_id
    
    configs = ConfigManager.load_configs()
    configs[config_id] = config
    ConfigManager.save_configs(configs)
    
    return jsonify({
        'message': 'Configuration saved successfully',
        'config': config
    })

@app.route('/api/lavalink/test-connection', methods=['POST'])
def test_lavalink_connection():
    """Test Lavalink connection endpoint."""
    config = request.json
    result = LavalinkConnectionManager.test_connection(config)
    return jsonify(result)

@app.route('/api/lavalink/configs/<config_id>', methods=['DELETE'])
def delete_lavalink_config(config_id):
    """Delete a specific Lavalink configuration."""
    configs = ConfigManager.load_configs()
    
    if config_id in configs:
        del configs[config_id]
        ConfigManager.save_configs(configs)
        return jsonify({'message': 'Configuration deleted successfully'})
    
    return jsonify({'error': 'Configuration not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)