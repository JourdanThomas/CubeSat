# CubeSat Distributed Computing Project

A distributed computing system using Raspberry Pi devices with automatic WiFi hotspot connection and task distribution.

## Overview

This project implements a master-slave distributed computing architecture where:
- **Master CubeSat**: Creates a WiFi hotspot and distributes computing tasks
- **Slave Devices**: Automatically connect to the hotspot and process distributed computing tasks

## Features

- **Automatic WiFi Hotspot**: Master device creates a WiFi network for slave devices
- **Auto-Connection**: Slave devices automatically detect and connect to the master's hotspot
- **Task Distribution**: Master distributes computing tasks across connected slave devices
- **Fault Tolerance**: Automatic reconnection and retry mechanisms
- **Real-time Monitoring**: Live status updates of connected devices and task progress

## Hardware Requirements

### Master Device (CubeSat)
- Raspberry Pi (3B+, 4, or newer)
- WiFi adapter (built-in or USB dongle)
- Power supply

### Slave Devices
- Raspberry Pi zero 
- Power supply
- MicroSD card

## Software Requirements

### Master Device
- Raspberry Pi OS (Raspbian) or Ubuntu
- Python 3.7+
- NetworkManager or hostapd
- Required Python packages (see requirements.txt)

### Slave Devices
- Raspberry Pi OS (Raspbian) or Ubuntu
- Python 3.7+
- NetworkManager or wpa_supplicant
- Required Python packages (see requirements.txt)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Distributed_Computing
```

### 2. Install Dependencies
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-scapy network-manager hostapd dnsmasq

# Install Python dependencies
pip3 install -r requirements.txt
```

### 3. Configure Network Settings

#### Master Device Configuration
Edit `master_hub.py` to match your network setup:
```python
# Hotspot settings
HOTSPOT_IFACE = "wlan1"  # WLAN1 for the USB dongle or WLAN0 for the build in wifi
HOTSPOT_SSID = "Master_CubeSat"  
HOTSPOT_PASSWORD = "raspberry"  
SUBNET = "192.168.50.1/24"  # Network range
```

#### Slave Device Configuration
Edit `slave.py` to match the master's settings:
```python
# Master hotspot settings (must match master_hub.py)
MASTER_SSID = "Master_CubeSat"
MASTER_PASSWORD = "raspberry"
MASTER_IP = "192.168.50.1"
WIFI_INTERFACE = "wlan0"  
```

## Usage

### Starting the Master Hub

1. **On the master Raspberry Pi:**
```bash
sudo python3 master_hub.py
```

2. **The master will:**
   - Start the WiFi hotspot
   - Begin listening for slave connections
   - Start distributing computing tasks
   - Monitor connected devices

### Starting Slave Devices

1. **On each slave Raspberry Pi:**
```bash
sudo python3 slave.py
```

2. **The slave will:**
   - Automatically scan for the master's WiFi network
   - Connect to the hotspot
   - Establish connection to the master's computing server
   - Begin processing distributed computing tasks

## Computing Tasks

The system currently supports these task types:

### 1. Prime Number Checking
- **Type**: `prime_check`
- **Data**: `{"number": 123456789}`
- **Purpose**: Check if a large number is prime

### 2. Fibonacci Calculation
- **Type**: `fibonacci`
- **Data**: `{"n": 1000}`
- **Purpose**: Calculate the nth Fibonacci number

### 3. Matrix Multiplication
- **Type**: `matrix_multiply`
- **Data**: `{"size": 100}`
- **Purpose**: Benchmark matrix operations

## Adding Custom Tasks

### On Master Device
Add new tasks to the queue:
```python
add_computing_task("custom_task", {"param1": "value1", "param2": "value2"})
```

### On Slave Device
Implement task processing in the `process_computing_task` method:
```python
elif task_type == "custom_task":
    result = self.process_custom_task(task_data)
```

## Network Configuration

### WiFi Interface Names
Common WiFi interface names:
- **Built-in WiFi**: `wlan0`
- **USB WiFi adapter**: `wlan1`, `wlan2`, etc.
- **Check your interface**: `ip link show`

### IP Address Ranges
Default network configuration:
- **Master IP**: 192.168.50.1
- **Network Range**: 192.168.50.0/24
- **Available IPs**: 192.168.50.2 - 192.168.50.254

## Troubleshooting

### Common Issues

#### 1. Hotspot Won't Start
```bash
# Check WiFi interface status
ip link show wlan1

# Restart NetworkManager
sudo systemctl restart NetworkManager

# Check for conflicting services
sudo systemctl status hostapd
sudo systemctl status dnsmasq
```

#### 2. Slave Can't Connect
```bash
# Check WiFi interface
ip link show wlan0

# Scan for networks
sudo iwlist wlan0 scan | grep -i "master_cubesat"

# Check connection status
nmcli device status
```

#### 3. Connection Drops
- Ensure stable power supply
- Check WiFi signal strength
- Verify network interface stability

### Debug Mode
Enable verbose logging by modifying the log level in both scripts.

## Security Considerations

- **WiFi Password**: Change default password in production
- **Network Isolation**: Consider VLANs for production use
- **Access Control**: Implement authentication for slave devices
- **Encryption**: Use WPA3 when possible

## Performance Optimization

### Task Distribution
- Implement load balancing based on device capabilities
- Add task priority queues
- Implement task result caching

### Network Optimization
- Use UDP for high-frequency communications
- Implement connection pooling
- Add network quality monitoring

## Monitoring and Logging

### Master Device Logs
- Device connection/disconnection events
- Task distribution and completion
- Network status and performance metrics

### Slave Device Logs
- Connection attempts and status
- Task processing progress
- Error conditions and recovery

## Future Enhancements

- **Web Dashboard**: Real-time monitoring interface
- **Task Scheduling**: Advanced task queuing and scheduling
- **Load Balancing**: Dynamic task distribution based on device load
- **Fault Recovery**: Automatic task redistribution on device failure
- **Scalability**: Support for larger device networks

