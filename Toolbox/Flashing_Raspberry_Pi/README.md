# Raspberry Pi Flashing via SD Card for the CubeSat
Only do this if really necessary as there is already a lot of modifications made on the base software.
It might be useful to make a backup of the image before doing any changes.

## **What You’ll Need**
- A **microSD card** (16GB minimum for CubeSats and the groundstation).
- A **computer** with an SD card slot or USB card reader.
- **Raspberry Pi Imager** or **Balena Etcher**(recommended) installed.
- The OS image file:

For the CubeSat use this version:
http://cubesatsim.org/download/cubesatsim.iso.zip

For the Grounstation use this version:
https://cubesatsim.org/download/Fox-in-box-v3.iso.gz

If you use balena etcher you don’t have to install the file on your computer as you can install from a link. If you are flashing multiple Raspberry you might want to install it locally first as it will be a lot faster. Raspberry Pi imager makes it easier to change the wifi setup but you might run into some issues as it sometimes forces you to change the username and this stops the software from running properly as it changes the name of the main folder of the OS.


---


## **Method 1: Manual Download + Balena Etcher**

1. **Download & Install Balena Etcher**  
   [https://etcher.balena.io/](https://etcher.balena.io/)

2. **Flash the SD Card**  
   - Open Etcher.  
   - Select the OS `.img` or `.zip` file you downloaded or use the link to download the  
   - Choose the SD card from the list.  
   - Click **Flash**.
   - Sometimes Balena etcher might show an error message, you can just ignore it and it will work fine. 

3. **Add SSH and Wi-Fi Config (Headless Setup)**
   You can check the other readme file in the Toolbox folder for more info.
   
   If you plan to run the Pi without a monitor:  
   - In the **boot** partition of the SD card, create an empty file named `ssh`.  
   - Add a `wpa_supplicant.conf` file with your Wi-Fi details:  
     ```conf
     country=US
     ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
     update_config=1

     network={
         ssid="YourNetworkName"
         psk="YourPassword"
     }
     ```

5. **Eject and Boot**  
   Safely eject the card, insert it into your Pi, and power it up.
   

---
## **Method 2: Using Raspberry Pi Imager**

1. **Download Raspberry Pi Imager**  
   Get it from the official website:  
   [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)  
   Install it on your computer.

2. **Insert Your SD Card**  
   Put the microSD card into the SD card reader and connect it to your computer.

3. **Open Raspberry Pi Imager**  
   Click:
   - **Choose OS** 
   - **Choose Storage** → Select your SD card.  

4. **(Optional) Enable SSH and Wi-Fi Before Flashing**  
   Press **Ctrl+Shift+X** (or `⌘+Shift+X` on Mac) to open **Advanced Options**:  
   - Enable SSH (set a password or use keys).  
   - Set Wi-Fi SSID, password, and country.  
   - Set hostname and locale.  

5. **Write the OS**  
   Click **Write**. Wait until it finishes and verify the write process.

6. **Eject the Card**  
   Once done, safely eject the SD card and insert it into your Raspberry Pi.



Made by Thomas Jourdan 08/2025