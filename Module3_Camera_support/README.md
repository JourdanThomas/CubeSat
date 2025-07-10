# Module 3 Camera support

	We are working with a base of the CubeSatSim, which was designed to function with standard module 2 Raspberry Pi cameras. However, our goal is to utilize a module 3 camera, which is not compatible with the default software for the CubeSatSim. This guide provides instructions on how to set up the NoIR Camera instead of the normal camera.
    
# How to setup a module 3 camera instead of the normal camera
## 1.The config file.
You can modify the configuration directly on the Raspberry Pi with the following command:
```
sudo nano /boot/config.txt
```
or via the sd Card on another computer.


You need to add
```
camera_auto_detect=1
dtoverlay=imx708
```

You can comment the line
```
#start_x=1
```
This controls whether the camera firmware and GPU support are enabled — specifically for the legacy camera stack.
This would allow to reduce boot time as we are not using a legacy camera

[Optional] You might need to replace (not necessary)
```
gpu_mem=128
```
By
```
gpu_mem=192
```
It sometimes allows for libcamera to work better but it can cause some issues in the main code

## 2. Connecting to wifi

Then you should start the pi with the SD card.
You can do 
```
sudo raspi-config
```
In the configuration menu:
- Go to System Options and set up the Wireless LAN to connect to WiFi.
- In Interface Options, enable SSH. This will make it easier to use and modify without having to disassemble the CubeSat to access HDMI.

You will need to reboot
```
sudo reboot
```
You can now connect via ssh
```
ssh pi@raspberrypi.local

```

## 3. Updating the software
Depending on the version of the CubeSat, you might need to update the software.

Update and upgrade the system:
```
sudo apt update
Sudo apt upgrade
```
You can also install the latest version of the CubeSatSim software via:
```
CubeSatSim/update
```
## 4. Installing libcamera

Install libcamera-apps:
```
sudo apt install libcamera-apps -y
```
You can use this command to test libcamera and see if the NoIR camera is detected
```
libcamera-hello
```
You can also test by taking a picture directly
```
libcamera-still -o test.jpg
```
If you were using ssh you can copy the picture to your computer to preview
```
scp pi@cubesatsim:~/test.jpg
```
## 4. Transmission
There are different versions of the CubeSatSim software and the following might change depending on the version.
First go to the CubeSatSim directory on the CubeSat
```
Cd CubeSatSim/
```
You will need to modify the file that enables data transmission.
It is either named `transmit.py` or `rpitx.py`
Depending on the name you wile need to use either to modify the file:
```
nano transmit.py
nano rpitx.py
```

Then find the lines: 
```
system(raspistill -o /home/pi/CubeSatSim/camera_out.jpg -w 320 -h 256)
```
And replace them with:

```
system("libcamera-still -o /home/pi/CubeSatSim/camera_out.jpg --width 320 --height 256 --timeout 1000")
```
You can now save by doing `ctrl+o`, `enter` then `ctrl+x`.
You will just need to reboot one last time and it should work.

To activate SSTV mode on the CubeSatSim, you can press the button until it blinks 4 time or do 








