#!/usr/bin/env python3
"""
Slave Raspberry Pi for Distributed Computing
Automatically connects to master hotspot and processes computing tasks
"""

import subprocess
import time
import socket
import json
import threading
import os
import sys
from datetime import datetime

# Master hotspot settings (must match master_hub.py)
MASTER_SSID = "Master_CubeSat"
MASTER_PASSWORD = "raspberry"
MASTER_IP = "192.168.50.1"
MASTER_PORT = 5000

# Network interface
WIFI_INTERFACE = "wlan0"

# Connection retry settings
MAX_RETRIES = 5
RETRY_DELAY = 10

 
class DistributedComputingSlave:
    def __init__(self):
        self.connected = False
        self.socket = None
        self.running = True
        
    def log(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def check_wifi_interface(self):
        """Check if WiFi interface exists and is up"""
        try:
            result = subprocess.run(
                ["ip", "link", "show", WIFI_INTERFACE],
                capture_output=True, text=True, check=True
            )
            return "UP" in result.stdout
        except subprocess.CalledProcessError:
            return False
            
    def scan_for_networks(self):
        """Scan for available WiFi networks"""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL", "device", "wifi", "list"],
                capture_output=True, text=True, check=True
            )
            networks = []
            for line in result.stdout.strip().split('\n'):
                if line and ':' in line:
                    ssid, signal = line.split(':', 1)
                    if ssid and ssid != "SSID":
                        networks.append(ssid.strip())
            return networks
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to scan networks: {e}")
            return []
            
    def connect_to_master(self):
        """Connect to the master's WiFi hotspot"""
        self.log(f"Attempting to connect to {MASTER_SSID}...")
        
        try:
            # First, try to connect using nmcli
            result = subprocess.run([
                "nmcli", "device", "wifi", "connect", MASTER_SSID,
                "password", MASTER_PASSWORD, "ifname", WIFI_INTERFACE
            ], capture_output=True, text=True, check=True)
            
            if "successfully activated" in result.stdout:
                self.log(f"Successfully connected to {MASTER_SSID}")
                return True
            else:
                self.log("Connection failed with nmcli")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log(f"nmcli connection failed: {e}")
            
            # Try alternative method using wpa_supplicant
            try:
                self.log("Trying wpa_supplicant method...")
                
                # Create wpa_supplicant configuration
                wpa_config = f"""ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1

network={{
    ssid="{MASTER_SSID}"
    psk="{MASTER_PASSWORD}"
    key_mgmt=WPA-PSK
}}"""
                
                with open("/tmp/wpa_supplicant.conf", "w") as f:
                    f.write(wpa_config)
                
                # Start wpa_supplicant
                subprocess.run([
                    "sudo", "wpa_supplicant", "-B", "-i", WIFI_INTERFACE,
                    "-c", "/tmp/wpa_supplicant.conf"
                ], check=True)
                
                # Get IP address
                subprocess.run([
                    "sudo", "dhclient", WIFI_INTERFACE
                ], check=True)
                
                self.log("Connected using wpa_supplicant")
                return True
                
            except subprocess.CalledProcessError as e2:
                self.log(f"wpa_supplicant also failed: {e2}")
                return False
                
    def wait_for_connection(self):
        """Wait for WiFi connection to be established"""
        max_wait = 60  # Wait up to 60 seconds
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                # Check if we have an IP address
                result = subprocess.run(
                    ["ip", "addr", "show", WIFI_INTERFACE],
                    capture_output=True, text=True, check=True
                )
                
                if "inet " in result.stdout:
                    self.log("WiFi connection established with IP address")
                    return True
                    
            except subprocess.CalledProcessError:
                pass
                
            time.sleep(2)
            wait_time += 2
            
        return False
        
    def get_current_ip(self):
        """Get current IP address"""
        try:
            result = subprocess.run(
                ["ip", "route", "get", "8.8.8.8"],
                capture_output=True, text=True, check=True
            )
            
            # Extract IP from route output
            for line in result.stdout.split('\n'):
                if "src" in line:
                    parts = line.split()
                    src_index = parts.index("src")
                    if src_index + 1 < len(parts):
                        return parts[src_index + 1]
                        
        except subprocess.CalledFailed:
            pass
            
        return None
        
    def connect_to_master_server(self):
        """Connect to the master's distributed computing server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((MASTER_IP, MASTER_PORT))
            self.log(f"Connected to master server at {MASTER_IP}:{MASTER_PORT}")
            return True
            
        except Exception as e:
            self.log(f"Failed to connect to master server: {e}")
            return False
            
    def process_computing_task(self, task):
        """Process a computing task and return result"""
        task_type = task.get('type')
        task_data = task.get('data', {})
        
        self.log(f"Processing task {task['id']}: {task_type}")
        
        try:
            if task_type == "prime_check":
                result = self.check_prime(task_data.get('number', 0))
            elif task_type == "fibonacci":
                result = self.calculate_fibonacci(task_data.get('n', 0))
            elif task_type == "matrix_multiply":
                result = self.matrix_multiply(task_data.get('size', 0))
            else:
                result = {"error": f"Unknown task type: {task_type}"}
                
            return {
                "task_id": task['id'],
                "result": result,
                "slave_id": self.get_slave_id(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "task_id": task['id'],
                "error": str(e),
                "slave_id": self.get_slave_id(),
                "timestamp": time.time()
            }
            
    def check_prime(self, n):
        """Check if a number is prime"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
            
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
        
    def calculate_fibonacci(self, n):
        """Calculate nth Fibonacci number"""
        if n <= 0:
            return 0
        if n == 1:
            return 1
            
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
        
    def matrix_multiply(self, size):
        """Simple matrix multiplication for benchmarking"""
        import random
        
        # Create random matrices
        matrix_a = [[random.random() for _ in range(size)] for _ in range(size)]
        matrix_b = [[random.random() for _ in range(size)] for _ in range(size)]
        
        # Multiply matrices
        result = [[0 for _ in range(size)] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    result[i][j] += matrix_a[i][k] * matrix_b[k][j]
                    
        return {"size": size, "completed": True}
        
    def get_slave_id(self):
        """Get unique slave identifier"""
        try:
            # Try to get Raspberry Pi serial number
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Serial'):
                        return line.split(':')[1].strip()
        except:
            pass
            
        # Fallback to hostname
        try:
            return subprocess.run(
                ["hostname"], capture_output=True, text=True, check=True
            ).stdout.strip()
        except:
            return "unknown"
            
    def run_computing_worker(self):
        """Main computing worker loop"""
        while self.running and self.socket:
            try:
                # Receive task from master
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                    
                task = json.loads(data)
                
                if task.get('type') == 'heartbeat':
                    # Send heartbeat response
                    self.socket.send(json.dumps({"type": "heartbeat", "slave_id": self.get_slave_id()}).encode())
                    continue
                    
                # Process the task
                result = self.process_computing_task(task)
                
                # Send result back to master
                self.socket.send(json.dumps(result).encode())
                
            except json.JSONDecodeError as e:
                self.log(f"Invalid JSON received: {e}")
            except Exception as e:
                self.log(f"Error in computing worker: {e}")
                break
                
    def main_loop(self):
        """Main connection and computing loop"""
        retry_count = 0
        
        while self.running and retry_count < MAX_RETRIES:
            try:
                # Check WiFi interface
                if not self.check_wifi_interface():
                    self.log(f"WiFi interface {WIFI_INTERFACE} is not available")
                    time.sleep(RETRY_DELAY)
                    retry_count += 1
                    continue
                    
                # Connect to master hotspot
                if not self.connect_to_master():
                    self.log("Failed to connect to master hotspot")
                    time.sleep(RETRY_DELAY)
                    retry_count += 1
                    continue
                    
                # Wait for connection to be established
                if not self.wait_for_connection():
                    self.log("Connection timeout")
                    time.sleep(RETRY_DELAY)
                    retry_count += 1
                    continue
                    
                # Get current IP
                current_ip = self.get_current_ip()
                if current_ip:
                    self.log(f"Current IP: {current_ip}")
                    
                # Connect to master server
                if not self.connect_to_master_server():
                    self.log("Failed to connect to master server")
                    time.sleep(RETRY_DELAY)
                    retry_count += 1
                    continue
                    
                # Reset retry count on successful connection
                retry_count = 0
                self.connected = True
                
                # Start computing worker
                self.log("Starting distributed computing worker...")
                self.run_computing_worker()
                
            except KeyboardInterrupt:
                self.log("Shutdown requested by user")
                break
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                time.sleep(RETRY_DELAY)
                retry_count += 1
                
        if retry_count >= MAX_RETRIES:
            self.log(f"Failed to connect after {MAX_RETRIES} attempts")
            
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        if self.socket:
            self.socket.close()
            
        # Disconnect from WiFi
        try:
            subprocess.run(["nmcli", "device", "disconnect", WIFI_INTERFACE], check=False)
        except:
            pass


def main():
    print("=== Raspberry Pi Distributed Computing Slave ===")
    print(f"Target SSID: {MASTER_SSID}")
    print(f"Master IP: {MASTER_IP}")
    print(f"Master Port: {MASTER_PORT}")
    print("=" * 50)
    
    slave = DistributedComputingSlave()
    
    try:
        slave.main_loop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        slave.cleanup()
        print("Slave shutdown complete")


if __name__ == "__main__":
    main()
