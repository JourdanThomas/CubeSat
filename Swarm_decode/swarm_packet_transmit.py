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
import os

logging.basicConfig(filename='/home/pi/CubeSatSim/sender3.log', level=logging.INFO, format='%(asctime)s - %(message)s')

LOG_DIR = "/home/pi/CubeSatSim/groundstation/MTU_swarm_logs"


# Function to read the configuration file
def read_config():
    config_path = os.path.join(LOG_DIR, "MTU_config.txt")
    cfg = {}
    try:
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    if k == "Frequencies":
                        # Parse frequencies as a list of ints
                        cfg[k] = [int(x) for x in v.strip().split()]
                    elif k == "Device_Count":
                        cfg[k] = int(v)
                    else:
                        cfg[k] = v
        return cfg
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        logging.error(f"Config file not found: {config_path}")
        return {}
    except Exception as e:
        print(f"Error reading config file: {e}")
        logging.error(f"Error reading config file: {e}")
        return {}
    


#cfg = read_config()
#host_ip = cfg.get("Host_IP")
#device_count = cfg.get("Device_Count")
#frequencies = cfg.get("Frequencies")


# Function to send configuration file via UDP
def send_config(host_ip, config_port=5000):
    """Send configuration file to the PC via UDP"""
    config_path = os.path.join(LOG_DIR, "MTU_config.txt")
    
    try:
        with open(config_path, 'r') as f:
            config_data = f.read()
        
        # Create UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Send config data
        s.sendto(config_data.encode('utf-8'), (host_ip, config_port))
        print(f"Configuration file sent to {host_ip}:{config_port}")
        logging.info(f"Configuration file sent to {host_ip}:{config_port}")
        
        s.close()
        return True
        
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        logging.error(f"Config file not found: {config_path}")
        return False
    except Exception as e:
        print(f"Error sending config: {e}")
        logging.error(f"Error sending config: {e}")
        return False


# Function to tail a file
def tail_f(filename):
    """Generator that yields new lines as they are written to the file."""
    try:
        with open(filename, "r") as f:
            # Go to end of file
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield line.rstrip('\n\r')  # Remove newline characters
    except FileNotFoundError:
        print(f"Log file not found: {filename}")
        logging.error(f"Log file not found: {filename}")
        return
    except Exception as e:
        print(f"Error reading log file {filename}: {e}")
        logging.error(f"Error reading log file {filename}: {e}")
        return

# get_ports function to generate a list of ports based on the device count
def get_ports(device_count, base_port=5001):
    """Return a list of ports for the given device count, starting from base_port."""
    return [base_port + i for i in range(device_count)]


# Function to create and manage socket connection
def create_socket_connection(host_ip, port, max_retries=5):
    """Create a socket connection with retry logic."""
    for attempt in range(max_retries):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)  # 10 second timeout
            s.connect((host_ip, port))
            print(f"Connected to {host_ip}:{port}")
            logging.info(f"Connected to {host_ip}:{port}")
            return s
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} - Could not connect to {host_ip}:{port}: {e}")
            logging.error(f"Connection attempt {attempt + 1} failed for {host_ip}:{port}: {e}")
            if s:
                s.close()
            time.sleep(2)  # Wait before retry
    return None


######################################################################
# Main function to handle connections and data transmission
######################################################################
def main():

    ####################################
    # Read configuration
    ####################################
    cfg = read_config()
    if not cfg:
        print("Failed to read configuration. Exiting.")
        return
    
    host_ip = cfg.get("Host_IP")
    device_count = cfg.get("Device_Count", 0)
    
    # If no host IP or device count is configured, exit the script
    if not host_ip or host_ip == "NotTransmitting" or device_count == 0:
        print(f"No transmission configured. Host_IP: {host_ip}, Device_Count: {device_count}")
        logging.info(f"No transmission configured. Host_IP: {host_ip}, Device_Count: {device_count}")
        return

    print(f"Starting transmission to {host_ip} for {device_count} devices")
    logging.info(f"Starting transmission to {host_ip} for {device_count} devices")
    ####################################
    # Send the configuration file
    ####################################
    print("Sending configuration file...")
    if not send_config(host_ip):
        print("Failed to send configuration file. Continuing anyway...")
    else:
        print("Configuration file sent successfully!")
        # Wait a bit for the PC to process the config and start data receivers
        time.sleep(5)

    ####################################
    # Create sockets for each device
    ####################################
    print("Creating sockets for each device...")
    ports = get_ports(device_count)
    sockets = []
    
    # Create a socket for each device
    for i in range(device_count):
        s = create_socket_connection(host_ip, ports[i])
        sockets.append(s)

    # Check if any sockets were successfully created
    active_sockets = [s for s in sockets if s is not None]
    if not active_sockets:
        print("No successful connections established. Exiting.")
        logging.error("No successful connections established")
        return
    ####################################
    # Create log files for each device
    ####################################

    # Create log file paths and check if they exist
    log_files = [os.path.join(LOG_DIR, f"device_{i}.log") for i in range(device_count)]
    tails = []
    
    # Initialize tails for each log file
    print("Initializing log file tails...")
    for i, log_file in enumerate(log_files):
        if os.path.exists(log_file):
            print(f"Monitoring log file: {log_file}")
            tails.append(tail_f(log_file))
        else:
            print(f"Log file does not exist: {log_file}")
            tails.append(None)

    # Main loop to read from log files and send data through sockets
    print("Starting data transmission...")
    logging.info("Starting data transmission")
    
    try:
        while True:
            for i in range(device_count):
                if tails[i] and sockets[i]:
                    try:
                        line = next(tails[i])
                        if line.strip():  # Only send non-empty lines
                            # Add newline back for transmission
                            data_to_send = line + '\n'
                            sockets[i].sendall(data_to_send.encode('utf-8'))
                            print(f"Device {i}: {line[:50]}..." if len(line) > 50 else f"Device {i}: {line}")
                    except StopIteration:
                        continue
                    except socket.error as e:
                        print(f"Socket error for device {i}: {e}")
                        logging.error(f"Socket error for device {i}: {e}")
                        if sockets[i]:
                            sockets[i].close()
                        # Try to reconnect
                        sockets[i] = create_socket_connection(host_ip, ports[i])
                    except Exception as e:
                        print(f"Error processing data from device {i}: {e}")
                        logging.error(f"Error processing data from device {i}: {e}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Received interrupt signal. Exiting...")
        logging.info("Received interrupt signal")
    except Exception as e:
        print(f"Unexpected error in main loop: {e}")
        logging.error(f"Unexpected error in main loop: {e}")
    finally:
        # Clean up all sockets
        print("Cleaning up connections...")
        for i, s in enumerate(sockets):
            if s:
                try:
                    s.close()
                    print(f"Closed connection for device {i}")
                except:
                    pass
        print("Cleanup complete.")


###################################
if __name__ == "__main__":
    main()