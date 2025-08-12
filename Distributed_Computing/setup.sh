#!/bin/bash

# CubeSat Distributed Computing Setup Script
# This script installs dependencies and configures the system

set -e

echo "=== CubeSat Distributed Computing Setup ==="
echo "This script will install dependencies and configure your system"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Detect OS
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "Could not detect OS"
    exit 1
fi

echo "Detected OS: $OS $VER"
echo ""

# Update package list
echo "Updating package list..."
apt update

# Install system dependencies
echo "Installing system dependencies..."
apt install -y python3 python3-pip python3-venv python3-dev

# Install network tools
echo "Installing network tools..."
apt install -y network-manager hostapd dnsmasq iw wireless-tools

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install scapy netifaces psutil

# Create virtual environment (optional but recommended)
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure NetworkManager
echo "Configuring NetworkManager..."
systemctl enable NetworkManager
systemctl start NetworkManager

# Configure hostapd and dnsmasq
echo "Configuring hostapd and dnsmasq..."
systemctl disable hostapd
systemctl disable dnsmasq

# Create configuration directory
mkdir -p /etc/cubesat
cp master_hub.py /etc/cubesat/
cp slave.py /etc/cubesat/
cp requirements.txt /etc/cubesat/

# Make scripts executable
chmod +x /etc/cubesat/master_hub.py
chmod +x /etc/cubesat/slave.py

# Create systemd service files
echo "Creating systemd service files..."

# Master service
cat > /etc/systemd/system/cubesat-master.service << EOF
[Unit]
Description=CubeSat Distributed Computing Master
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/etc/cubesat
ExecStart=/usr/bin/python3 /etc/cubesat/master_hub.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Slave service
cat > /etc/systemd/system/cubesat-slave.service << EOF
[Unit]
Description=CubeSat Distributed Computing Slave
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/etc/cubesat
ExecStart=/usr/bin/python3 /etc/cubesat/slave.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the master hub:"
echo "  sudo systemctl start cubesat-master"
echo "  sudo systemctl enable cubesat-master"
echo ""
echo "To start a slave device:"
echo "  sudo systemctl start cubesat-slave"
echo "  sudo systemctl enable cubesat-slave"
echo ""
echo "To check status:"
echo "  sudo systemctl status cubesat-master"
echo "  sudo systemctl status cubesat-slave"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u cubesat-master -f"
echo "  sudo journalctl -u cubesat-slave -f"
echo ""
echo "Remember to configure the network settings in the Python files before starting!"
echo ""
