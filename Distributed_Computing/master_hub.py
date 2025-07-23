import subprocess
from scapy.all import ARP, Ether, srp
import time

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


def is_raspberry_pi(mac):
    mac = mac.lower()
    return any(mac.startswith(prefix) for prefix in RASPBERRY_MAC_PREFIXES)


def start_hotspot():
    print("Starting hotspot...")
    try:
        subprocess.run([
            "nmcli", "dev", "wifi", "hotspot",
            "ifname", HOTSPOT_IFACE,
            "ssid", HOTSPOT_SSID,
            "password", HOTSPOT_PASSWORD
        ], check=True)
        print("Hotspot started!")
    except subprocess.CalledProcessError as e:
        print("Failed to start hotspot:", e)
        exit(1)


def scan_for_raspberry_pis(ip_range=SUBNET):
    print(f"Scanning {ip_range} for Raspberry Pi devices...")

    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=2, verbose=0)[0]

    raspberry_devices = []
    other_devices = []

    for _, received in result:
        if is_raspberry_pi(received.hwsrc):
            raspberry_devices.append({'ip': received.psrc, 'mac': received.hwsrc})
        else:
            other_devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return raspberry_devices


if __name__ == "__main__":
    print("Starting...")
    start_hotspot()

    # Wait for devices to connect
    print("Waiting for devices to connect...")
    time.sleep(10)


    while True:

        devices = scan_for_raspberry_pis()

        if devices:
            print("Raspberry Pi devices found:")
            for i, device in enumerate(devices, 1):
                print(f"{i}. IP: {device['ip']}, MAC: {device['mac']}")
        else:
            print("No Raspberry Pi devices found.")

        time.sleep(10)



