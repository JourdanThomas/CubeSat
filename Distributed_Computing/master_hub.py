import subprocess
from scapy.all import ARP, Ether, srp
import time
import socket
import threading
import json

# Known Raspberry Pi MAC address prefixes
RASPBERRY_MAC_PREFIXES = [
    "b8:27:eb",
    "dc:a6:32",
    "e4:5f:01",
    "d8:3a:dd"
]

# Hotspot settings
HOTSPOT_IFACE = "wlan1"
HOTSPOT_SSID = "Master_CubeSat"
HOTSPOT_PASSWORD = "raspberry"
SUBNET = "192.168.50.1/24"  # Adjust if different
MASTER_PORT = 5000

# Store connected devices and their status
connected_devices = {}
task_queue = []
results = {}

def is_raspberry_pi(mac):
    mac = mac.lower()
    return any(mac.startswith(prefix) for prefix in RASPBERRY_MAC_PREFIXES)


def start_hotspot():
    print("Starting hotspot...")
    try:
        # Stop any existing hotspot
        subprocess.run(["nmcli", "radio", "wifi", "off"], check=False)
        time.sleep(1)
        subprocess.run(["nmcli", "radio", "wifi", "on"], check=False)
        time.sleep(2)
        
        # Create hotspot
        subprocess.run([
            "nmcli", "dev", "wifi", "hotspot",
            "ifname", HOTSPOT_IFACE,
            "ssid", HOTSPOT_SSID,
            "password", HOTSPOT_PASSWORD
        ], check=True)
        print(f"Hotspot '{HOTSPOT_SSID}' started successfully!")
        print(f"SSID: {HOTSPOT_SSID}")
        print(f"Password: {HOTSPOT_PASSWORD}")
        print(f"Interface: {HOTSPOT_IFACE}")
    except subprocess.CalledProcessError as e:
        print("Failed to start hotspot:", e)
        print("Trying alternative method...")
        try:
            # Alternative method using hostapd
            subprocess.run([
                "sudo", "systemctl", "start", "hostapd"
            ], check=True)
            print("Hotspot started using hostapd!")
        except subprocess.CalledProcessError as e2:
            print("Failed to start hotspot using hostapd:", e2)
            exit(1)


def scan_for_raspberry_pis(ip_range=SUBNET):
    print(f"Scanning {ip_range} for Raspberry Pi devices...")

    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=2, verbose=0)[0]
    print(f"Found {len(result)} devices")
    
    raspberry_devices = []
    other_devices = []

    for _, received in result:
        if is_raspberry_pi(received.hwsrc):
            raspberry_devices.append({'ip': received.psrc, 'mac': received.hwsrc})
        else:
            other_devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return raspberry_devices


def handle_client_connection(client_socket, address):
    """Handle individual client connections for distributed computing tasks"""
    print(f"New connection from {address}")
    
    try:
        while True:
            # Send task to client
            if task_queue:
                task = task_queue.pop(0)
                client_socket.send(json.dumps(task).encode())
                
                # Wait for result
                result_data = client_socket.recv(1024).decode()
                if result_data:
                    result = json.loads(result_data)
                    results[task['id']] = result
                    print(f"Received result for task {task['id']}: {result}")
            else:
                # Send heartbeat
                client_socket.send(json.dumps({"type": "heartbeat"}).encode())
                time.sleep(1)
                
    except Exception as e:
        print(f"Client {address} disconnected: {e}")
    finally:
        client_socket.close()


def start_computing_server():
    """Start the distributed computing server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', MASTER_PORT))
        server_socket.listen(5)
        print(f"Distributed computing server listening on port {MASTER_PORT}")
        
        while True:
            client_socket, address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client_connection, 
                args=(client_socket, address)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()


def add_computing_task(task_type, data):
    """Add a new computing task to the queue"""
    task_id = len(task_queue) + 1
    task = {
        'id': task_id,
        'type': task_type,
        'data': data,
        'timestamp': time.time()
    }
    task_queue.append(task)
    print(f"Added task {task_id}: {task_type}")
    return task_id


if __name__ == "__main__":
    print("=== Master CubeSat Distributed Computing Hub ===")
    
    # Start the WiFi hotspot
    start_hotspot()
    
    # Start the distributed computing server in a separate thread
    server_thread = threading.Thread(target=start_computing_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for devices to connect
    print("Waiting for devices to connect...")
    time.sleep(10)
    
    # Add some sample computing tasks
    add_computing_task("prime_check", {"number": 123456789})
    add_computing_task("fibonacci", {"n": 1000})
    add_computing_task("matrix_multiply", {"size": 100})

    while True:
        devices = scan_for_raspberry_pis()
        
        if devices:
            print(f"\nRaspberry Pi devices found ({len(devices)}):")
            for i, device in enumerate(devices, 1):
                print(f"{i}. IP: {device['ip']}, MAC: {device['mac']}")
                
            print(f"\nTask queue: {len(task_queue)} tasks")
            print(f"Completed results: {len(results)}")
            
        else:
            print("No Raspberry Pi devices found.")
            
        time.sleep(30)  # Scan every 30 seconds



