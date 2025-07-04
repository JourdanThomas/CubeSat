# How to setup the Swarm communication mode
The Swarm Communication
## First install
### Ground Station

#### Files
on the desktop of the Raspberry Pi of the Ground Station
**You should have a file named « swarm.desktop » **
With the following contents:

```
[Desktop Entry]
Version=1.0
Name=Swarm Packet Decode using Direwolf
GenericName=Decodes swarm packet using rtl_fm and Direwolf
Comment=APRS signals
Exec=/home/pi/CubeSatSim/groundstation/swarm_packet.sh
Icon=/home/pi/Icons/aprs.png
Terminal=true
Type=Application
Categories=Network;HamRadio;
Keywords=APRS;ISS;
```


You will also need a program in /home/pi/CubeSatSim/groundstation
This program is named: « swarm_packet.sh" 

The contents are:

#### Serial number issue
By default, all antennas come with the same serial number, which makes it difficult to use multiple units simultaneously.
To identify each antenna, you can run:
`rtl_test` 
Then, to assign a unique serial number, plug in only one antenna at a time and run:
`sudo rtl_eeprom -s NEW_SERIAL_NUMBER`


#### Number of loop_back devices
##### Setup ALSA Loopback for 4 Devices
You need 4 loopback devices so Direwolf instances don’t clash on audio devices.
Modify /etc/modprobe.d/alsa-loopback.conf like this:
`options snd-aloop enable=1,1,1,1 index=2,3,4,5 pcm_substreams=2,2,2,2`
You might not have the permissions to change the configuration file directly so you can use:
`echo "options snd-aloop enable=1,1,1,1 index=2,3,4,5 pcm_substreams=2,2,2,2" | sudo tee /etc/modprobe.d/alsa-loopback.conf`




This creates 4 loopback sound cards at indexes 2, 3, 4, and 5, each with 2 substreams.
##### Reload ALSA Loopback Module
Apply changes:
```
sudo modprobe -r snd-aloop
sudo modprobe snd-aloop
```
Check devices with:
`aplay -l`


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






