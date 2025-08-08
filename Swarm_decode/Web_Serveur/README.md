# Web Server for Project CubeSat

**This web server provides real-time visualization of CubeSat data received from a Raspberry Pi-based ground station. It is designed to be run locally on a PC connected to the same Wi-Fi network as the ground station.
When properly set up, you'll be able to monitor attitude, sensor data, communication status, and more via a local browser interface.**


# Setup Instructions
## 1. Ensure Network Connection
Make sure your PC is connected to the same Wi-Fi as the ground station (Raspberry Pi).

# 2. Configure Server IP (Optional)
The server will automatically detect its local IP and display it in the terminal.

If needed, you can manually specify the PC's IP address by modifying the following line in pc.py:


This folder contains all the necessary files to launch the website. It's important to note that this isn't just a collection of HTML pages; it's a functioning server. To run the server, ensure that you're connected to the Wi-Fi network and specify the IP address in the "pc_ip = 192.168.xxx.xxx" field within the 'pc.py' script.

Once this configuration is set, launch the server from the terminal or command prompt by navigating to your 'server' directory using the appropriate path:
local_project_path\serveur> python .\pc.py

After executing this command, the server will start and display a message like:

WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://172.28.24.28:8080
Press CTRL+C to quit

To access the website, open your web browser and enter the following URL:
http://localhost:8080/index
This will direct you to the project's homepage.


# Open the Web Interface
In your browser, go to:
```
http://localhost:8080/index
```
Or use the actual IP shown in the terminal output:
```
http://192.168.1.45:8080/index
```
You should now see the CubeSat web dashboard.

# Related Features
`/get_data` – Returns all telemetry in JSON

`/get_device_data/<id>` – Data from a specific CubeSat

`/get_status` – Server and device status

`/get_config` – Current system configuration

# Authors
Developed by Thomas Jourdan and M'hamed Chetouane
July 2025, MTU

