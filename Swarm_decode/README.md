# Swarm decode
This program enables decoding of multiple CubeSats simultaneously using RTL-SDR devices, loopback audio interfaces, and Direwolf for APRS demodulation.

It also supports optional transmission of decoded data over the network and is designed to work on a Raspberry Pi-based Ground Station.

The BPSK decoding mode is still a work in progress and does not work for now
The link between the web interface and the data is not completely debugged

# I- First install
## I.1- Ground Station

### Files
on the desktop of the Raspberry Pi of the Ground Station
You should have a file named « swarm.desktop »
You will be able to start the program by using this shortcut

Place the following files in:
/home/pi/CubeSatSim/groundstation/MTU_swarm/
├── swarm_packet.sh
├── swarm_packet_transmit.py
└── (optional) BPSK_decode.py


### Configure ALSA Loopback Devices
#### Setup ALSA Loopback for 4 Devices
You need (at least) 4 loopback devices so Direwolf instances don’t clash on audio devices.
Modify /etc/modprobe.d/alsa-loopback.conf like this:
`options snd-aloop enable=1,1,1,1 index=2,3,4,5 pcm_substreams=2,2,2,2`
You might not have the permissions to change the configuration file directly so you can use:
`echo "options snd-aloop enable=1,1,1,1 index=2,3,4,5 pcm_substreams=2,2,2,2" | sudo tee /etc/modprobe.d/alsa-loopback.conf`

This creates 4 loopback sound cards at indexes 2, 3, 4, and 5, each with 2 substreams.
#### Reload ALSA Loopback Module
Apply changes:
```
sudo modprobe -r snd-aloop
sudo modprobe snd-aloop
```
Check devices with:
`aplay -l`

## I.2- Webserver host

### Files
Place the following files in a suitable directory:
```
pc.py                        # Main server script
templates/                  # Folder containing HTML pages
└── index.html
    Reaction_Wheels.html
    Wifi_Communication.html
    ...
data/
└── received_config.txt      # Created automatically
└── data.txt                 # Created automatically
```


Run the Flask server using
```
python3 pc.py
```
Once running, the server will:
-Display a QR code with the web interface URL
-Receive configuration and log data
-Serve live data via a browser-accessible interface

## I.3- Setting up the Cubesats
### Changing the Callsign
To change the callsign of a CubeSat, use the following command:
`CubeSatSim/config -c`

### Changing the frequency
To modify the transmission (TX) and reception (RX) frequencies, use:
`CubeSatSim/config -F`
By default:
TX frequency = 343.9 kHz
RX frequency = 435 kHz

### Changing the mode to APRS
To change the mode to APRS of each cubesat you need to use
`CubeSatSim/config -a`
Or you can press the button until it blinks once and then release.


# II - Starting the program

On the Raspberry Pi desktop, double-click swarm.desktop.

You’ll be prompted to:
-Select decode mode (APRS / BPSK)
-Enter frequencies for each RTL-SDR
-(Optional) Enable network transmission to the web server

The program:
-Creates and manages log files for each device
-Starts rtl_fm + Direwolf or BPSK processing
-If enabled, launches swarm_packet_transmit.py to send data to the PC


# III - Troubleshooting

## Executable files
If you make changes to the program and if you get 
`Invalid desktop entry file: '/home/pi/Desktop/swarm.desktop'`
you should do
```
chmod +x /home/pi/CubeSatSim/groundstation/MTU_swarm/swarm_packet.sh
chmod +x /home/pi/Desktop/swarm.desktop
```
## Serial number issue
By default, all antennas come with the same serial number, which makes it difficult to use multiple units simultaneously.
To identify each antenna, you can run:
`rtl_test` 
Then, to assign a unique serial number, plug in only one antenna at a time and run:
`sudo rtl_eeprom -s NEW_SERIAL_NUMBER`
Once you have defined a different serial number for all antennas it should work.

# IV - Web Interface Endpoints
After launching pc.py, access the server in a browser via the displayed IP.
Available routes:
/index, /Live_Status, etc. – Visual interfaces
/get_data – JSON dump of all recent data
/get_device_data/<id> – Data from a specific CubeSat
/get_config – Current configuration
/get_status – System diagnostics

You can find more explanations in this repo in the `pictures` folder
You can find examples of a config file and the log files in the `example` folder

# About
This system was developed by Thomas Jourdan (and M'hamed Chetouane for the html and js) at MTU, August 2025.
