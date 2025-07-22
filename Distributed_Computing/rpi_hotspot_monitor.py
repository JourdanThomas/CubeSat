#!/usr/bin/env python3
"""
Raspberry Pi Hotspot Creator and Device Monitor
Creates a WiFi hotspot and continuously monitors connected devices
"""

import subprocess
import time
import json
import os
import sys
from datetime import datetime
import threading
import signal
import re

class HotspotManager:
    def __init__(self, ssid="RaspberryPi-Hotspot", password="raspberry123", interface="wlan0"):
        self.ssid = ssid
        self.password = password
        self.interface = interface
        self.connected_devices = {}
        self.running = True
        
    def check_root(self):
        """Check if running with root privileges"""
        if os.geteuid() != 0:
            print("This script requires root privileges. Please run with sudo.")
            sys.exit(1)
    
    def install_dependencies(self):
        """Install required packages if not present"""
        packages = ["hostapd", "dnsmasq"]
        for package in packages:
            try:
                subprocess.run(["which", package], check=True, capture_output=True)
                print(f"✓ {package} is installed")
            except subprocess.CalledProcessError:
                print(f"Installing {package}...")
                subprocess.run(["apt", "update"], check=True)
                subprocess.run(["apt", "install", "-y", package], check=True)
    
    def create_hostapd_config(self):
        """Create hostapd configuration file"""
        config_content = f"""
interface={self.interface}
driver=nl80211
ssid={self.ssid}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={self.password}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
        with open("/etc/hostapd/hostapd.conf", "w") as f:
            f.write(config_content.strip())
        print("✓ Created hostapd configuration")
    
    def create_dnsmasq_config(self):
        """Create dnsmasq configuration for DHCP"""
        # Backup original config
        if os.path.exists("/etc/dnsmasq.conf") and not os.path.exists("/etc/dnsmasq.conf.backup"):
            subprocess.run(["cp", "/etc/dnsmasq.conf", "/etc/dnsmasq.conf.backup"])
        
        config_content = f"""
interface={self.interface}
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
"""
        with open("/etc/dnsmasq.conf", "w") as f:
            f.write(config_content.strip())
        print("✓ Created dnsmasq configuration")
    
    def configure_interface(self):
        """Configure the wireless interface"""
        commands = [
            ["ip", "link", "set", "dev", self.interface, "down"],
            ["ip", "addr", "add", "192.168.4.1/24", "dev", self.interface],
            ["ip", "link", "set", "dev", self.interface, "up"]
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Command {' '.join(cmd)} failed: {e}")
        
        print("✓ Configured network interface")
    
    def enable_ip_forwarding(self):
        """Enable IP forwarding for internet sharing"""
        with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
            f.write("1")
        
        # Add iptables rules for NAT (assuming eth0 for internet)
        nat_rules = [
            ["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "eth0", "-j", "MASQUERADE"],
            ["iptables", "-A", "FORWARD", "-i", "eth0", "-o", self.interface, "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"],
            ["iptables", "-A", "FORWARD", "-i", self.interface, "-o", "eth0", "-j", "ACCEPT"]
        ]
        
        for rule in nat_rules:
            try:
                subprocess.run(rule, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                pass  # Rule might already exist
        
        print("✓ Enabled IP forwarding and NAT")
    
    def start_services(self):
        """Start hostapd and dnsmasq services"""
        try:
            # Stop services first
            subprocess.run(["systemctl", "stop", "hostapd"], capture_output=True)
            subprocess.run(["systemctl", "stop", "dnsmasq"], capture_output=True)
            
            # Start services
            subprocess.run(["systemctl", "start", "hostapd"], check=True)
            subprocess.run(["systemctl", "start", "dnsmasq"], check=True)
            
            print("✓ Started hostapd and dnsmasq services")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to start services: {e}")
            return False
    
    def get_connected_devices(self):
        """Get list of connected devices using multiple methods"""
        devices = {}
        
        # Method 1: Parse DHCP leases
        try:
            with open("/var/lib/dhcp/dhcpd.leases", "r") as f:
                content = f.read()
                # Parse DHCP leases (simplified)
                leases = re.findall(r'lease (\d+\.\d+\.\d+\.\d+) {[^}]+client-hardware-ethernet ([^;]+);[^}]+binding state active;', content, re.DOTALL)
                for ip, mac in leases:
                    devices[mac.strip()] = {"ip": ip, "method": "dhcp"}
        except FileNotFoundError:
            pass
        
        # Method 2: Check ARP table
        try:
            result = subprocess.run(["arp", "-a"], capture_output=True, text=True, check=True)
            for line in result.stdout.split('\n'):
                if '192.168.4.' in line:
                    match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\) at ([a-fA-F0-9:]{17})', line)
                    if match:
                        ip, mac = match.groups()
                        devices[mac] = {"ip": ip, "method": "arp"}
        except subprocess.CalledProcessError:
            pass
        
        # Method 3: Check hostapd station list (if available)
        try:
            result = subprocess.run(["hostapd_cli", "-i", self.interface, "list_sta"], 
                                  capture_output=True, text=True, check=True)
            for line in result.stdout.split('\n'):
                if ':' in line and len(line.strip()) == 17:  # MAC address format
                    mac = line.strip()
                    if mac not in devices:
                        devices[mac] = {"ip": "unknown", "method": "hostapd"}
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return devices
    
    def get_device_vendor(self, mac):
        """Get device vendor from MAC address (simplified)"""
        # This is a basic implementation. For full vendor lookup, you'd need OUI database
        oui_map = {
            "b8:27:eb": "Raspberry Pi",
            "dc:a6:32": "Raspberry Pi",
            "e4:5f:01": "Raspberry Pi",
            "28:cd:c1": "Apple",
            "3c:15:c2": "Apple",
            "00:1b:63": "Apple"
        }
        
        mac_prefix = mac[:8].lower()
        return oui_map.get(mac_prefix, "Unknown")
    
    def monitor_devices(self):
        """Continuously monitor connected devices"""
        print(f"\n🔍 Monitoring devices on hotspot '{self.ssid}'...")
        print("=" * 70)
        
        while self.running:
            try:
                current_devices = self.get_connected_devices()
                
                # Check for new connections
                for mac, info in current_devices.items():
                    if mac not in self.connected_devices:
                        vendor = self.get_device_vendor(mac)
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"📱 NEW DEVICE CONNECTED:")
                        print(f"   Time: {timestamp}")
                        print(f"   MAC:  {mac}")
                        print(f"   IP:   {info['ip']}")
                        print(f"   Vendor: {vendor}")
                        print(f"   Method: {info['method']}")
                        print("-" * 50)
                        
                        self.connected_devices[mac] = {
                            "ip": info["ip"],
                            "vendor": vendor,
                            "connected_at": timestamp,
                            "method": info["method"]
                        }
                
                # Check for disconnections
                disconnected = []
                for mac in self.connected_devices:
                    if mac not in current_devices:
                        disconnected.append(mac)
                
                for mac in disconnected:
                    device_info = self.connected_devices[mac]
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"📵 DEVICE DISCONNECTED:")
                    print(f"   Time: {timestamp}")
                    print(f"   MAC:  {mac}")
                    print(f"   Was:  {device_info['ip']} ({device_info['vendor']})")
                    print("-" * 50)
                    del self.connected_devices[mac]
                
                # Show current status every 30 seconds
                if int(time.time()) % 30 == 0:
                    print(f"📊 Status at {datetime.now().strftime('%H:%M:%S')}: {len(self.connected_devices)} devices connected")
                    if self.connected_devices:
                        for mac, info in self.connected_devices.items():
                            print(f"   • {mac} ({info['ip']}) - {info['vendor']}")
                
                time.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error monitoring devices: {e}")
                time.sleep(5)
    
    def cleanup(self):
        """Clean up and stop services"""
        print("\n🧹 Cleaning up...")
        self.running = False
        
        try:
            subprocess.run(["systemctl", "stop", "hostapd"], capture_output=True)
            subprocess.run(["systemctl", "stop", "dnsmasq"], capture_output=True)
            
            # Restore original dnsmasq config
            if os.path.exists("/etc/dnsmasq.conf.backup"):
                subprocess.run(["cp", "/etc/dnsmasq.conf.backup", "/etc/dnsmasq.conf"])
            
            # Reset interface
            subprocess.run(["ip", "addr", "flush", "dev", self.interface], capture_output=True)
            subprocess.run(["ip", "link", "set", "dev", self.interface, "down"], capture_output=True)
            
            print("✓ Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def run(self):
        """Main execution function"""
        print("🔥 Raspberry Pi Hotspot Manager")
        print("=" * 40)
        
        # Setup signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print("\n⚠️  Shutdown requested...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            self.check_root()
            print("✓ Running with root privileges")
            
            self.install_dependencies()
            self.create_hostapd_config()
            self.create_dnsmasq_config()
            self.configure_interface()
            self.enable_ip_forwarding()
            
            if self.start_services():
                print(f"🚀 Hotspot '{self.ssid}' is now active!")
                print(f"📶 Password: {self.password}")
                print(f"🌐 Gateway IP: 192.168.4.1")
                
                # Start monitoring in a separate thread
                monitor_thread = threading.Thread(target=self.monitor_devices)
                monitor_thread.daemon = True
                monitor_thread.start()
                
                # Keep main thread alive
                while self.running:
                    time.sleep(1)
            else:
                print("✗ Failed to start hotspot services")
                
        except Exception as e:
            print(f"✗ Error: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    # Configuration - modify these as needed
    SSID = "RaspberryPi-Hotspot"
    PASSWORD = "raspberry123"  # Must be at least 8 characters
    INTERFACE = "wlan0"  # Usually wlan0 for Pi 3
    
    hotspot = HotspotManager(ssid=SSID, password=PASSWORD, interface=INTERFACE)
    hotspot.run()