# Raspberry Pi Wi-Fi and SSH Setup Guide

This guide explains two ways to connect your Raspberry Pi to Wi-Fi and
enable SSH access.


## **Method 1: Using `sudo raspi-config` (On the Pi Itself)**

1.  **Boot your Raspberry Pi** with a monitor, keyboard, and mouse
    connected.

2.  Open a terminal and run:

    ``` bash
    sudo raspi-config
    ```

3.  Navigate to:

        System Options → Wireless LAN

4.  Enter your **Wi-Fi SSID** and **Password**.

5.  To enable SSH, go to:

        Interface Options → SSH → Enable

6.  Exit the menu and reboot:

    ``` bash
    sudo reboot
    ```

Your Pi should now be connected to Wi-Fi, and SSH will be enabled.



## **Method 2: Editing Files on the SD Card (Headless Setup)**

If you don't have a monitor/keyboard for your Pi, you can preconfigure
Wi-Fi and SSH by editing files on the SD card.

1.  **Insert the SD card** into your computer after flashing Raspberry
    Pi OS.
2.  In the **boot** partition:
    -   Create a file named `ssh` (no extension) to enable SSH.

    -   Create a file named `wpa_supplicant.conf` with the following
        content:

        ``` conf
        country=US
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1

        network={
            ssid="YourNetworkName"
            psk="YourPassword"
        }
        ```

    -   Replace `YourNetworkName` and `YourPassword` with your actual
        Wi-Fi credentials.

    -   Change `country=US` to your country code (e.g., `GB` for the
        UK).
3.  Safely eject the SD card and insert it into the Raspberry Pi.
4.  Power up the Pi. It will connect to Wi-Fi and have SSH enabled.


## **Connecting via SSH**

Once your Raspberry Pi is on the network, find its IP address (e.g., via
your router or by running `ping raspberrypi.local`).

From your computer, run:

``` bash
ssh pi@<IP_ADDRESS>
```
Or on a CubSat you can use
``` bash
ssh pi@cubesatsim
```
However you might be limited if there is multiple CubeSats on the same network

Default password is:

    raspberry


Made by Thomas Jourdan 08/2025
