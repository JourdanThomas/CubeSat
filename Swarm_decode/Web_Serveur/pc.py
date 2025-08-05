# coding=utf-8

#######################################################
# MTU            pc.py
# script to run the web server for the CubeSat Swarm project
## This script sets up a Flask web server to serve data from the ground station,
# allowing users to view data from multiple devices.
#######################################################
# made by Thomas Jourdan and M'hamed Chetouane
# 07/2025
#######################################################


import socket
import threading
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
import time
import pyqrcode



################################################
#     Configuration of PC's IP address and port
################################################
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

pc_ip = get_local_ip()   # IP address of the Wi-Fi shared with the Raspberry Pi
pc_port = 8080

# Configuration for receiving data
config_port = 5000
base_data_port = 5001  # Should match the base_port in swarm_packet_transmit.py
device_count = 0  # Will be set when config is received
data_receivers = {}  # Dictionary to store data from each device

# Configuration file path (will be created when received)
config_file = '/Users/thomasjourdan/Documents/GitHub/CubeSat/Swarm_decode/data/received_config.txt'

ascii_art = """  ____      _          ____        _   ____  _
 / ___|   _| |__   ___/ ___|  __ _| |_/ ___|(_)_ __ ___
| |  | | | | '_ \ / _ \___ \ / _` | __\___ \| | '_ ` _ \\
| |__| |_| | |_) |  __/___) | (_| | |_ ___) | | | | | | |
\____\__,_|_.__/ \___|____/ \__,_|\__|____/|_|_| |_| |_|
\ \      / /__| |__    ___  ___ _ ____   _____ _ __
 \ \ /\ / / _ \ '_ \  / __|/ _ \ '__\ \ / / _ \ '__|
  \ V  V /  __/ |_) | \__ \  __/ |   \ V /  __/ |
   \_/\_/ \___|_.__/  |___/\___|_|    \_/ \___|_|
"""

print(ascii_art)

print("")
print("the PC IP is:",pc_ip)
print("the PC port is:",pc_port)
print("")

# Location of the text file where you want to save the data
output_file = '/Users/thomasjourdan/Documents/GitHub/CubeSat/Swarm_decode/data/data.txt'

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

qr = pyqrcode.create(content='http://'+str(pc_ip)+':'+str(pc_port) )
print(qr.terminal(module_color='white', background='black'))

################################################
#     Configuration for Flask web server
################################################

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
CORS(app, resources={r"/get_data": {"origins": "*"}})


################################################
#        Routes for different pages
################################################

@app.route('/')
#main page
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/Live_Status')
def live_status():
    return render_template('Live_Status.html') 

@app.route('/Reaction_Wheels')
def reaction_wheels():
    return render_template('Reaction_Wheels.html')

@app.route('/Wifi_Communication')
def wifi_communication():
    return render_template('Wifi_Communication.html')

@app.route('/3D_Visualisation')
def d_visualisation():
    return render_template('3D_Visualisation.html')

@app.route('/Meteor_Detection')
def meteor_detection():
    return render_template('Meteor_Detection.html')

@app.route('/Youtube_Link_RW')
def youtube_link_rw():
    return render_template('Youtube_Link_RW.html')

@app.route('/Youtube_Link_3D')
def youtube_link_3d():
    return render_template('Youtube_Link_3D.html')

@app.route('/Youtube_Link_Meteor')
def youtube_link_meteor():
    return render_template('Youtube_Link_Meteor.html')

@app.route('/Youtube_Link_WIFI')
def youtube_link_wifi():
    return render_template('Youtube_Link_WIFI.html')

@app.route('/Project_Link_Meteor')
def project_link_meteor():
    return render_template('Project_Link_Meteor.html')

@app.route('/Project_Link_3D')
def project_link_3d():
    return render_template('Project_Link_3D.html')

@app.route('/Project_Link_RW')
def project_link_rW():
    return render_template('Project_Link_RW.html')

@app.route('/Project_Link_WIFI')
def project_link_wifi():
    return render_template('Project_Link_WIFI.html')




################################################################################################

################################################################################################

# Create a route to retrieve the IP (useful to get the IP from another device)
@app.route('/get_ip', methods=['GET'])
def get_ip():
    return jsonify({"ip_port": str(pc_ip)+':'+str(pc_port)})


# Create a route to retrieve data from all devices
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        with open(output_file, 'r') as f:
            data = f.read().splitlines()
            str_data = []

            # If the file has more than 50 lines, take the last 50 lines
            if len(data) > 50:
                data = data[-50:]

            # Split each line using comma as a delimiter
            for d in data:
                values = d.split(',')
                str_data.append(values)

        return jsonify(str_data)
    
    except FileNotFoundError:
        error_message = f"Error: The file '{output_file}' can't be found."
        print(error_message)
        return jsonify({"error": f"The file '{output_file}' can't be found."}), 404 

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)
        return jsonify({"error": f"There has been an error : {str(e)}"}), 500


# Route to get data from a specific device
@app.route('/get_device_data/<int:device_id>', methods=['GET'])
def get_device_data(device_id):
    try:
        if device_id in data_receivers:
            # Return the last few lines of data for this specific device
            device_data = data_receivers[device_id][-50:] if len(data_receivers[device_id]) > 50 else data_receivers[device_id]
            return jsonify({"device_id": device_id, "data": device_data})
        else:
            return jsonify({"error": f"Device {device_id} not found or not connected"}), 404
    except Exception as e:
        return jsonify({"error": f"Error retrieving device data: {str(e)}"}), 500


# Route to get configuration information
@app.route('/get_config', methods=['GET'])
def get_config():
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = f.read()
            return jsonify({"config": config_data})
        else:
            return jsonify({"error": "Config file not received yet"}), 404
    except Exception as e:
        return jsonify({"error": f"Error reading config: {str(e)}"}), 500


# Route to get system status
@app.route('/get_status', methods=['GET'])
def get_status():
    return jsonify({
        "pc_ip": pc_ip,
        "device_count": device_count,
        "connected_devices": list(data_receivers.keys()),
        "config_port": config_port,
        "base_data_port": base_data_port,
        "config_received": os.path.exists(config_file)
    })


################################################
#     Network receivers for configuration and data
################################################

def receive_config():
    """Receive configuration file via UDP on config_port"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((pc_ip, config_port))
    print(f"Config receiver listening on {pc_ip}:{config_port}...")
    
    while True:
        try:
            data, addr = s.recvfrom(4096)  # Larger buffer for config file
            received_data = data.decode('utf-8')
            print(f"[CONFIG] Received config from {addr}: {len(received_data)} bytes")
            
            # Save config to file
            with open(config_file, 'w') as f:
                f.write(received_data)
            
            print(f"[CONFIG] Configuration saved to {config_file}")
            
            # Parse device count from config
            global device_count
            for line in received_data.split('\n'):
                if 'Device_Count=' in line:
                    device_count = int(line.split('=')[1])
                    print(f"[CONFIG] Device count set to: {device_count}")
                    # Start data receivers for each device
                    start_data_receivers()
                    break
                    
        except Exception as e:
            print(f"[CONFIG] Error receiving config: {e}")


def receive_device_data(device_id, port):
    """Receive data from a specific device via TCP"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((pc_ip, port))
        server_socket.listen(1)
        print(f"[DEVICE {device_id}] Data receiver listening on {pc_ip}:{port}...")
        
        # Initialize data storage for this device
        data_receivers[device_id] = []
        
        while True:
            try:
                client_socket, addr = server_socket.accept()
                print(f"[DEVICE {device_id}] Connected to {addr}")
                
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    received_line = data.decode('utf-8').strip()
                    if received_line:
                        print(f"[DEVICE {device_id}] Received: {received_line[:50]}...")
                        
                        # Store data for this device
                        data_receivers[device_id].append(received_line)
                        
                        # Keep only last 200 lines per device to prevent memory issues
                        if len(data_receivers[device_id]) > 200:
                            data_receivers[device_id] = data_receivers[device_id][-200:]

                        # Also write to main output file with device identifier
                        with open(output_file, 'a') as f:
                            f.write(f"device_{device_id},{received_line}\n")
                            
            except Exception as e:
                print(f"[DEVICE {device_id}] Connection error: {e}")
                time.sleep(1)  # Wait before trying to accept new connections
                
    except Exception as e:
        print(f"[DEVICE {device_id}] Socket error: {e}")
    finally:
        server_socket.close()


def start_data_receivers():
    """Start TCP receivers for each device"""
    global device_count
    if device_count > 0:
        print(f"Starting data receivers for {device_count} devices...")
        for i in range(device_count):
            port = base_data_port + i
            threading.Thread(
                target=receive_device_data, 
                args=(i, port), 
                daemon=True
            ).start()


################################################
#     Main application startup
################################################

if __name__ == '__main__':
    # Start config receiver
    config_thread = threading.Thread(target=receive_config, daemon=True)
    config_thread.start()
    
    print(f"Server starting on {pc_ip}:{pc_port}")
    print("Available endpoints:")
    print(f"  - Configuration: GET {pc_ip}:{pc_port}/get_config")
    print(f"  - All data: GET {pc_ip}:{pc_port}/get_data")
    print(f"  - Device data: GET {pc_ip}:{pc_port}/get_device_data/<device_id>")
    print(f"  - System status: GET {pc_ip}:{pc_port}/get_status")
    
    # Run the Flask server
    app.run(host='0.0.0.0', port=pc_port, debug=False)