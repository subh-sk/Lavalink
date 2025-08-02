import json
import logging
import os
import platform
import subprocess
import uuid

import docker
import psutil
import websocket  # Add this for WebSocket connection testing
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('lavalink_dashboard.log'),
                        logging.StreamHandler()
                    ])

# Configuration storage
CONFIG_FILE = 'lavalink_configs.json'

class LavaLinkConfigManager:
    @staticmethod
    def load_configs():
        try:
            if not os.path.exists(CONFIG_FILE):
                return {}
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading configs: {e}")
            return {}

    @staticmethod
    def save_configs(configs):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(configs, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving configs: {e}")

    @staticmethod
    def generate_connection_details():
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get('lavalink')
            container.reload()
            
            # Try to get the actual IP and port
            network_settings = container.attrs['NetworkSettings']
            ports = network_settings.get('Ports', {})
            
            # Default fallback
            host = network_settings.get('IPAddress', 'localhost')
            port = 2333

            # If using port mapping
            if '2333/tcp' in ports:
                port_mapping = ports['2333/tcp'][0]
                host = port_mapping.get('HostIp', host)
                port = int(port_mapping.get('HostPort', port))

            return {
                'host': host,
                'port': port,
                'password': 'admin123',
                'secure': False
            }
        except Exception as e:
            logging.error(f"Error generating connection details: {e}")
            return {
                'host': 'localhost',
                'port': 2333,
                'password': 'admin123',
                'secure': False
            }

class LavaLinkManager:
    @staticmethod
    def get_system_info():
        return {
            'os': platform.system(),
            'os_release': platform.release(),
            'python_version': platform.python_version(),
            'cpu_cores': psutil.cpu_count(),
            'total_memory': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            'available_memory': f"{psutil.virtual_memory().available / (1024**3):.2f} GB"
        }

    @staticmethod
    def get_lavalink_logs(lines=100):
        try:
            log_path = './logs/spring.log'
            if not os.path.exists(log_path):
                return "Log file not found"
            
            with open(log_path, 'r') as log_file:
                logs = log_file.readlines()[-lines:]
                return ''.join(logs)
        except Exception as e:
            logging.error(f"Error reading logs: {e}")
            return f"Error reading logs: {e}"

    @staticmethod
    def test_lavalink_connection(host, port, password):
        """
        Attempt to establish a WebSocket connection to Lavalink
        """
        try:
            # Construct WebSocket URL
            ws_url = f"ws://{host}:{port}/websocket"
            
            # Create WebSocket connection
            ws = websocket.create_connection(
                ws_url, 
                header={
                    "Authorization": password,
                    "User-Agent": "Lavalink-Dashboard-Tester/1.0"
                },
                timeout=5  # 5 second timeout
            )
            
            # Send a test message
            ws.send(json.dumps({
                "op": "info",
                "reconnect": False
            }))
            
            # Wait for response
            response = ws.recv()
            ws.close()
            
            return {
                'success': True,
                'message': 'Connection successful',
                'details': {
                    'host': host,
                    'port': port,
                    'response': json.loads(response)
                }
            }
        except Exception as e:
            logging.error(f"Lavalink connection test failed: {e}")
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'details': {
                    'host': host,
                    'port': port,
                    'error': str(e)
                }
            }

    @staticmethod
    def manage_lavalink(action):
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get('lavalink')
            
            actions = {
                'start': container.start,
                'stop': container.stop,
                'restart': container.restart
            }
            
            if action in actions:
                actions[action]()
                logging.info(f"Lavalink {action}ed successfully")
                return True
            return False
        except Exception as e:
            logging.error(f"Error {action}ing Lavalink: {e}")
            return False

    @staticmethod
    def get_lavalink_status():
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get('lavalink')
            container.reload()
            
            return {
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else 'Unknown',
                'created': container.attrs['Created'],
                'ports': container.attrs['NetworkSettings']['Ports'],
                'running': container.status == 'running'
            }
        except Exception as e:
            logging.error(f"Error getting Lavalink status: {e}")
            return {'status': 'error', 'running': False, 'message': str(e)}

    @staticmethod
    def get_connection_configs():
        configs = LavaLinkConfigManager.load_configs()
        return configs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(LavaLinkManager.get_lavalink_status())

@app.route('/api/system-info')
def get_system_info():
    return jsonify(LavaLinkManager.get_system_info())

@app.route('/api/logs')
def get_logs():
    lines = request.args.get('lines', default=100, type=int)
    return jsonify({'logs': LavaLinkManager.get_lavalink_logs(lines)})

@app.route('/api/control', methods=['POST'])
def control_lavalink():
    action = request.json.get('action')
    result = LavaLinkManager.manage_lavalink(action)
    return jsonify({'success': result})

@app.route('/api/lavalink/connection', methods=['GET'])
def get_lavalink_connection():
    """
    Get Lavalink connection details
    """
    connection_details = LavaLinkConfigManager.generate_connection_details()
    return jsonify(connection_details)

@app.route('/api/lavalink/configs', methods=['GET', 'POST'])
def manage_lavalink_configs():
    """
    Manage Lavalink connection configurations
    """
    if request.method == 'GET':
        # Retrieve saved configurations
        configs = LavaLinkConfigManager.load_configs()
        return jsonify(configs)
    
    elif request.method == 'POST':
        # Add or update a configuration
        config = request.json
        
        # Validate input
        if not all(key in config for key in ['name', 'host', 'port', 'password']):
            return jsonify({'error': 'Invalid configuration'}), 400
        
        # Generate unique ID if not provided
        config_id = config.get('id', str(uuid.uuid4()))
        config['id'] = config_id
        
        # Load existing configs
        configs = LavaLinkConfigManager.load_configs()
        
        # Update or add configuration
        configs[config_id] = config
        
        # Save configurations
        LavaLinkConfigManager.save_configs(configs)
        
        return jsonify({
            'message': 'Configuration saved successfully',
            'config': config
        })

@app.route('/api/lavalink/configs/<config_id>', methods=['DELETE'])
def delete_lavalink_config(config_id):
    """
    Delete a specific Lavalink configuration
    """
    configs = LavaLinkConfigManager.load_configs()
    
    if config_id in configs:
        del configs[config_id]
        LavaLinkConfigManager.save_configs(configs)
        return jsonify({'message': 'Configuration deleted successfully'})
    
    return jsonify({'error': 'Configuration not found'}), 404

@app.route('/api/lavalink/test-connection', methods=['POST'])
def test_lavalink_connection():
    """
    Test Lavalink connection
    """
    config = request.json
    
    # Validate input
    if not all(key in config for key in ['host', 'port', 'password']):
        return jsonify({'error': 'Invalid connection details'}), 400
    
    # Perform actual connection test
    result = LavaLinkManager.test_lavalink_connection(
        config['host'], 
        config['port'], 
        config['password']
    )
    
    return jsonify(result)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)