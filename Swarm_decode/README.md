# Swarm decode
This program enables decoding of multiple CubeSats simultaneously using RTL-SDR devices, loopback audio interfaces, and Direwolf for APRS demodulation.

It also supports optional transmission of decoded data over the network and is designed to work on a Raspberry Pi-based Ground Station.



# How to setup the Swarm communication mode
The Swarm Communication




# I- First install
## I.1- Ground Station

### Files
on the desktop of the Raspberry Pi of the Ground Station
You should have a file named « swarm.desktop »
You will be able to start the program by using this shortcut

You will also need to add in `/home/pi/CubeSatSim/groundstation/MTU_swarm/` the following files:
`swarm_packet.sh`
`swarm_packet_transmit.py`
(Optional, in development) BPSK_decode.py – For future BPSK support

### Number of loop_back devices
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
This 
### Files



pc.py                        # Main server script
templates/                  # Folder containing HTML pages
└── index.html
    Reaction_Wheels.html
    Wifi_Communication.html
    ...
data/
└── received_config.txt      # Created automatically
└── data.txt                 # Created automatically






## Setting up the Cubesats
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


# Starting the program
You can start the program by using 




# Troubleshooting
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






