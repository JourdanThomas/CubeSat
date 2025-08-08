# CubeSatSim Interaction Guide

This document explains how to interact with the CubeSatSim using the pushbutton and how to control it using commands from the Raspberry Pi.

##  Powering Up and Down

- **To power up** the CubeSatSim, remove the RBF pin. The green LED should light up within 30 seconds, followed by the blue LED when transmitting starts.
- **To shut down**, use the button until the green LED starts slow blinking, then release. Once the CubeSatSim shuts down, insert the RBF pin to keep it off.

---

## Pushbutton Functions

The pushbutton supports multiple functions based on how long you hold it. Watch the green LED blinks to choose the action:

| Action | LED Blinks | Description |
|--------|------------|-------------|
| Tap (no hold) | - | Reboot CubeSatSim |
| Hold and release after 1 blink | 1 | Switch to **APRS/AFSK** mode |
| Hold and release after 2 blinks | 2 | Switch to **FSK/DUV** mode |
| Hold and release after 3 blinks | 3 | Switch to **BPSK** mode |
| Hold and release after 4 blinks | 4 | Switch to **SSTV** mode |
| Hold and release after 5 blinks | 5 | Switch to **CW (Morse Code)** mode |
| Hold and release after slow blink | Slow | **Shutdown** CubeSatSim |
| Hold and release after even slower blink | Very Slow | Toggle **Command & Control (RF)** and reboot |

---

## Raspberry Pi Command Line Interface

You can also control the CubeSatSim via terminal:

### Basic Commands

```bash
CubeSatSim/config -c     # Set callsign
CubeSatSim/config -l     # Set latitude and longitude
CubeSatSim/config -F     # Set transmission frequency
CubeSatSim/config -a     # APRS mode
CubeSatSim/config -f     # FSK/DUV mode
CubeSatSim/config -b     # BPSK mode
CubeSatSim/config -s     # SSTV mode
CubeSatSim/config -m     # CW mode
CubeSatSim/config -T     # Toggle RF Command and Control
```

### Telemetry & Sensor Tools

```bash
CubeSatSim/telem         # Show current sensor readings
CubeSatSim/config -S     # I2C bus scan
CubeSatSim/config -t     # Toggle simulated telemetry
```

### Service Control

```bash
sudo systemctl stop cubesatsim     # Stop CubeSatSim
sudo systemctl stop rpitx          # Stop transmitter

sudo systemctl disable cubesatsim  # Prevent auto-start on boot
sudo systemctl enable cubesatsim   # Re-enable auto-start
```

---

## Transmitting and Listening

- Default transmit frequency is **434.9 MHz FM**.
- CW ID is transmitted first as **HI HI DE CALLSIGN**.
- Use **FoxTelem**, **MMSSTV**, or **Direwolf** to decode telemetry depending on mode.

---

## Resources

- CubeSatSim Wiki: [https://github.com/alanbjohnston/CubeSatSim/wiki](https://github.com/alanbjohnston/CubeSatSim/wiki)
- Telemetry spreadsheet: [https://cubesatsim.org/telem](https://cubesatsim.org/telem)

---

Made by Thomas Jourdan 08/2025