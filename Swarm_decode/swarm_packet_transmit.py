# coding=utf-8

#######################################################
# MTU            Swarm_packet_transmit.py
# script to transmit data from the ground station to the web server
#
# This script reads the configuration file, connects to the specified host IP and ports,
# and sends data from log files for each device.
# It uses a generator to tail the log files and sends new lines as they are written.
# The script runs indefinitely until interrupted, handling multiple devices and their respective log files.
#######################################################
# made by Thomas Jourdan
# 07/2025
#######################################################



import socket
import time
import logging

logging.basicConfig(filename='/home/pi/CubeSatSim/sender3.log', level=logging.INFO, format='%(asctime)s - %(message)s')

LOG_DIR = "/home/pi/CubeSatSim/groundstation/MTU_swarm_logs"


# Function to read the configuration file
def read_config():
    import os
    config_path = os.path.join(LOG_DIR, "MTU_config.txt")
    cfg = {}
    with open(config_path) as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                if k == "Frequencies":
                    # Parse frequencies as a list of ints
                    cfg[k] = [int(x) for x in v.strip().split()]
                elif k == "Device_Count":
                    cfg[k] = int(v)
                else:
                    cfg[k] = v
    return cfg

#cfg = read_config()
#host_ip = cfg.get("Host_IP")
#device_count = cfg.get("Device_Count")
#frequencies = cfg.get("Frequencies")

# Function to tail a file
def tail_f(filename):
    """Generator that yields new lines as they are written to the file."""
    with open(filename, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

# get_ports function to generate a list of ports based on the device count
def get_ports(device_count, base_port=5001):
    """Return a list of ports for the given device count, starting from base_port."""
    return [base_port + i for i in range(device_count)]

# Main function to handle connections and data transmission
def main():
	# Read configuration
    cfg = read_config()
    host_ip = cfg.get("Host_IP")
    device_count = cfg.get("Device_Count", 0)
	# If no host IP or device count is configured, exit the script
    if not host_ip or host_ip == "NotTransmitting" or device_count == 0:
        print("No host IP or device count configured. Exiting.")
        return

    ports = get_ports(device_count)
    sockets = []

	# Create a socket for each device
    for i in range(device_count):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host_ip, ports[i]))
            sockets.append(s)
            print(f"Connected to {host_ip}:{ports[i]}")
        except Exception as e:
            print(f"Could not connect to {host_ip}:{ports[i]}: {e}")
            sockets.append(None)

    log_files = [os.path.join(LOG_DIR, f"device_{i}.log") for i in range(device_count)]
    tails = []
	# Initialize tails for each log file
    print("Initializing log file tails...")
    for i, log_file in enumerate(log_files):
        if os.path.exists(log_file):
            tails.append(tail_f(log_file))
        else:
            tails.append(None)

	# Main loop to read from log files and send data through sockets
    print("Starting data transmission...")
    try:
        while True:
            for i in range(device_count):
                if tails[i] and sockets[i]:
                    try:
                        line = next(tails[i])
                        sockets[i].sendall(line.encode())
                    except StopIteration:
                        continue
                    except Exception as e:
                        print(f"Error sending data from device {i}: {e}")
                        sockets[i].close()
                        sockets[i] = None
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        for s in sockets:
            if s:
                s.close()

if __name__ == "__main__":
    main()