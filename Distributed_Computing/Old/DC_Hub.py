import subprocess
import time
import re

def start_hotspot():
    print("[+] Setting static IP...")
    subprocess.run(['sudo', 'ip', 'link', 'set', 'wlan0', 'down'])
    subprocess.run(['sudo', 'ip', 'addr', 'add', '192.168.4.1/24', 'dev', 'wlan0'])
    subprocess.run(['sudo', 'ip', 'link', 'set', 'wlan0', 'up'])

    print("[+] Enabling IP forwarding...")
    subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.ip_forward=1'])

    print("[+] Starting dnsmasq...")
    subprocess.run(['sudo', 'dnsmasq', '--conf-file=/etc/dnsmasq.conf'])

    print("[+] Starting hostapd...")
    subprocess.Popen(['sudo', 'hostapd', '/etc/hostapd/hostapd.conf'])

def get_connected_devices():
    output = subprocess.check_output("arp -a", shell=True).decode()
    devices = re.findall(r'\((.*?)\)', output)
    return devices

if __name__ == "__main__":
    start_hotspot()

    print("[+] Monitoring connected devices...")
    try:
        while True:
            devices = get_connected_devices()
            print(f"[+] Connected devices: {devices}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
        subprocess.run(['sudo', 'killall', 'hostapd'])
        subprocess.run(['sudo', 'killall', 'dnsmasq'])
