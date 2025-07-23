#!/usr/bin/env python3
"""
Hostapd Troubleshooting Script for Raspberry Pi
Diagnoses common issues and provides fixes
"""

import subprocess
import os
import sys
import re

def run_command(cmd, description=""):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_wifi_interface():
    """Check WiFi interface capabilities"""
    print("=== CHECKING WIFI INTERFACE ===")
    
    # Check if wlan0 exists
    success, stdout, stderr = run_command(["ip", "link", "show"])
    if "wlan0" in stdout:
        print("OK: wlan0 interface found")
    else:
        print("ERROR: wlan0 interface not found")
        print("Available interfaces:")
        print(stdout)
        return False
    
    # Check wireless capabilities
    print("\nChecking wireless capabilities...")
    success, stdout, stderr = run_command(["iw", "list"])
    if success:
        if "AP" in stdout:
            print("OK: WiFi interface supports Access Point mode")
        else:
            print("WARNING: AP mode might not be supported")
            print("Supported modes:", re.findall(r'\* (\w+)', stdout))
    else:
        print("Could not check wireless capabilities")
    
    return True

def check_hostapd_config():
    """Check hostapd configuration"""
    print("\n=== CHECKING HOSTAPD CONFIGURATION ===")
    
    config_path = "/etc/hostapd/hostapd.conf"
    if not os.path.exists(config_path):
        print("ERROR: hostapd.conf not found")
        return False
    
    print("OK: hostapd.conf exists")
    
    # Read and validate config
    try:
        with open(config_path, 'r') as f:
            config = f.read()
        print("Config contents:")
        print(config)
        
        # Check for common issues
        if "driver=nl80211" not in config:
            print("WARNING: driver not set to nl80211")
        if "interface=" not in config:
            print("ERROR: interface not specified")
        if "ssid=" not in config:
            print("ERROR: ssid not specified")
            
    except Exception as e:
        print("ERROR reading config:", str(e))
        return False
    
    return True

def test_hostapd_directly():
    """Test hostapd directly to see detailed error"""
    print("\n=== TESTING HOSTAPD DIRECTLY ===")
    
    # First, make sure interface is down
    run_command(["ip", "link", "set", "dev", "wlan0", "down"])
    
    print("Testing hostapd configuration...")
    success, stdout, stderr = run_command(["hostapd", "-t", "/etc/hostapd/hostapd.conf"])
    
    if success:
        print("OK: Configuration test passed")
    else:
        print("ERROR: Configuration test failed")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return False
    
    # Try running hostapd for a few seconds
    print("\nTrying to start hostapd (will stop after 5 seconds)...")
    try:
        process = subprocess.Popen(
            ["hostapd", "/etc/hostapd/hostapd.conf"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a few seconds
        import time
        time.sleep(5)
        
        if process.poll() is None:
            print("OK: hostapd started successfully")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("ERROR: hostapd failed to start")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False
            
    except Exception as e:
        print("ERROR: Could not test hostapd:", str(e))
        return False

def check_conflicting_services():
    """Check for conflicting services"""
    print("\n=== CHECKING CONFLICTING SERVICES ===")
    
    services_to_check = [
        "wpa_supplicant",
        "NetworkManager",
        "dhcpcd"
    ]
    
    for service in services_to_check:
        success, stdout, stderr = run_command(["systemctl", "is-active", service])
        if "active" in stdout:
            print("WARNING: " + service + " is running (might conflict)")
        else:
            print("OK: " + service + " is not active")

def check_rfkill():
    """Check if WiFi is blocked by rfkill"""
    print("\n=== CHECKING RFKILL STATUS ===")
    
    success, stdout, stderr = run_command(["rfkill", "list"])
    if success:
        print("rfkill status:")
        print(stdout)
        if "Soft blocked: yes" in stdout or "Hard blocked: yes" in stdout:
            print("WARNING: WiFi might be blocked by rfkill")
            print("Try: sudo rfkill unblock wifi")
        else:
            print("OK: WiFi not blocked by rfkill")
    else:
        print("Could not check rfkill status")

def generate_working_config():
    """Generate a minimal working hostapd config"""
    print("\n=== GENERATING MINIMAL CONFIG ===")
    
    minimal_config = """# Minimal hostapd configuration for Raspberry Pi
interface=wlan0
driver=nl80211
ssid=RaspberryPi-Test
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=raspberry123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP"""
    
    try:
        with open("/etc/hostapd/hostapd_minimal.conf", "w") as f:
            f.write(minimal_config)
        print("Created minimal config: /etc/hostapd/hostapd_minimal.conf")
        print("Test with: sudo hostapd /etc/hostapd/hostapd_minimal.conf")
        return True
    except Exception as e:
        print("ERROR: Could not create minimal config:", str(e))
        return False

def check_kernel_modules():
    """Check if necessary kernel modules are loaded"""
    print("\n=== CHECKING KERNEL MODULES ===")
    
    success, stdout, stderr = run_command(["lsmod"])
    required_modules = ["cfg80211", "mac80211"]
    
    for module in required_modules:
        if module in stdout:
            print("OK: " + module + " module loaded")
        else:
            print("WARNING: " + module + " module not found")

def main():
    """Main troubleshooting function"""
    if os.geteuid() != 0:
        print("Please run with sudo for complete diagnosis")
        sys.exit(1)
    
    print("RASPBERRY PI HOSTAPD TROUBLESHOOTING")
    print("=" * 50)
    
    # Stop hostapd if running
    run_command(["systemctl", "stop", "hostapd"])
    
    # Run all checks
    check_wifi_interface()
    check_hostapd_config()
    check_conflicting_services()
    check_rfkill()
    check_kernel_modules()
    test_hostapd_directly()
    generate_working_config()
    
    print("\n=== RECOMMENDATIONS ===")
    print("1. Try the minimal config: sudo hostapd /etc/hostapd/hostapd_minimal.conf")
    print("2. If that works, gradually add back features")
    print("3. Check 'sudo journalctl -u hostapd' for detailed error logs")
    print("4. Consider stopping NetworkManager: sudo systemctl stop NetworkManager")
    print("5. Make sure country code is set: sudo raspi-config -> Localisation -> WLAN Country")

if __name__ == "__main__":
    main()