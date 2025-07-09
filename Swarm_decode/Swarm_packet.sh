#!/bin/bash
#######################################################
# MTU            swarm_packet.sh
# script to auto decode packet using rtl_fm and Direwolf
# made by Thomas Jourdan 
#07/2025
#######################################################



#creating the log folder
mkdir -p /home/pi/CubeSatSim/groundstation/MTU_swarm_logs
#deleting old log files
rm -f /home/pi/CubeSatSim/groundstation/MTU_swarm_logs/device*


echo
echo "MTU Nimbus SWARM DECODE"
echo "V1.11"


sudo modprobe snd-aloop
#Stopping all processes that might use the devices
sudo systemctl stop openwebrx
sudo systemctl stop rtl_tcp
pkill -o chromium &>/dev/null
sudo killall -9 rtl_fm &>/dev/null
sudo killall -9 direwolf &>/dev/null
sudo killall -9 aplay &>/dev/null
sudo killall -9 qsstv &>/dev/null
sudo killall -9 rtl_tcp &>/dev/null
sudo killall -9 java &>/dev/null
sudo killall -9 CubicSDR &>/dev/null
sudo killall -9 zenity &>/dev/null

#######################################################
# Ask user for decoding mode
#######################################################
mode=$(zenity --list --title="Choose Decode Mode" --radiolist \
  --column="Pick" --column="Mode" TRUE "APRS" FALSE "BPSK" 2>/dev/null)

if [[ -z "$mode" ]]; then
  echo "No mode selected. Exiting..."
  exit 1
fi

echo "Selected mode: $mode"
echo

#######################################################
# Detect RTL-SDR devices
#######################################################
device_count=$(rtl_test -t 2>&1 | grep -c "^  [0-9]:")
if [ "$device_count" -eq 0 ]; then
  echo "No RTL-SDR devices found. Exiting..."
  sleep 3
  exit 1
fi

echo "Found $device_count RTL-SDR device(s)."



#######################################################
# Ask user for frequency for each device
#######################################################
declare -a frequencies
for ((i=0; i<device_count; i++)); do
  freq=$(zenity --entry --title="Frequency Selection" --text="Enter frequency for device $i (MHz like 436.5 or kHz like 145800):" 2>/dev/null)
  if [[ -z "$freq" ]]; then
    echo "No frequency entered for device $i. Exiting..."
    exit 1
  fi
  # Convert MHz to Hz if needed
  if [[ "$freq" == *.* ]]; then
    freq=$(echo "$freq*1000000" | bc | awk '{printf "%d", $1}')
  else
    freq="${freq}000"
  fi
  frequencies[$i]=$freq
done

echo
echo "Note: Due to SDR tuning offsets, the actual tuned frequency may differ slightly."
echo


#######################################################
# Transmission Configuration
#
# The user is prompted to decide whether to transmit data
# to a remote host (e.g., for live decoding or data relay).
#
# CHOICES:
# 1. If the user clicks "Yes":
#    - They are asked to enter a host IP address.
#    - If they enter a valid IP, it is saved to the config.
#    - If they enter "0", the script attempts to reuse the
#      previous IP stored in MTU_config.txt.
#    - If no previous IP is found, transmission is disabled.
#
# 2. If the user clicks "No":
#    - Transmission is disabled.
#    - "Host_IP=NotTransmitting" is stored in MTU_config.txt
#      to indicate no IP is in use.
#
# This logic ensures the script always writes a complete
# and valid configuration file, even if transmission is off.
#######################################################
zenity --question --text="Do you want to transmit data to the network?" --ok-label="Yes" --cancel-label="No"
transmit=$?


#
if [[ "$transmit" -eq 0 ]]; then
  host_ip=$(zenity --entry --title="Host IP" --text="Enter the host IP address to transmit to (or 0 to keep last):" 2>/dev/null)

  if [[ -z "$host_ip" ]]; then
    echo "No IP entered. Transmission disabled."
    host_ip="NotTransmitting"
  elif [[ "$host_ip" == "0" ]]; then
    if [[ -f /home/pi/CubeSatSim/groundstation/MTU_swarm_logs/MTU_config.txt ]]; then
      host_ip=$(grep "^Host_IP=" /home/pi/CubeSatSim/groundstation/MTU_swarm_logs/MTU_config.txt | cut -d'=' -f2)
      echo "Keeping previous IP: $host_ip"
    else
      echo "No previous IP found. Transmission disabled."
      sleep 6
      host_ip="NotTransmitting"
    fi
  else
    echo "New IP entered: $host_ip"
  fi
else
  echo "Transmission not enabled."
fi
#######################################################
# Save configuration to MTU_config.txt
#######################################################
config_file="/home/pi/CubeSatSim/groundstation/MTU_swarm_logs/MTU_config.txt"
{
  echo "Host_IP=$host_ip"
  echo "Device_Count=$device_count"
  echo -n "Frequencies="
  printf "%s " "${frequencies[@]}"
  echo
} > "$config_file"
echo "Configuration saved to $config_file"
#######################################################
# Start transmitting
#######################################################
if [[ "$host_ip" != "NotTransmitting" ]]; then
  python3 /home/pi/CubeSatSim/groundstation/MTU_swarm/swarm_packet_transmit.py
fi





#######################################################
# if APRS Create separate Direwolf config files for each device
#######################################################
#Create a config foler, should already exist 
if [[ "$mode" == "APRS" ]]; then
  mkdir -p /home/pi/direwolf

  for ((i=0; i<device_count; i++)); do
    loop_index=$((2 + i))  # Loopback sound card index (2, 3, 4, 5...)
    config_file="/home/pi/direwolf/mtudwconfig$((i+1))"
    cat <<EOF > "$config_file"
ADEVICE plughw:${loop_index},1
CHANNEL 0
MYCALL NOCALL
MODEM 1200
AGWPORT $((8000 + i))
KISSPORT $((8100 + i))
LOGDIR /home/pi/CubeSatSim/groundstation/MTU_swarm_logs
EOF
  done
fi

#######################################################
# Start decoding on each RTL-SDR
#######################################################
# Start decoding per device
for ((i=0; i<device_count; i++)); do
  freq=${frequencies[$i]}
  loop_index=$((2 + i)) # assign correct loopback for each device
  log_file="/home/pi/CubeSatSim/groundstation/MTU_swarm_logs/device_${i}.log"
  echo "Starting decoding on device $i at frequency ${freq} Hz..."

  if [[ "$mode" == "APRS" ]]; then
    conf_file="/home/pi/direwolf/mtudwconfig$((i+1))"

    echo "Starting decoding on device $i at frequency ${freq} Hz using config $conf_file..."
    rtl_fm -d $i -M fm -f $freq -s 48k | aplay -D hw:${loop_index},0,0 -r 48000 -t raw -f S16_LE -c 1 &
    direwolf -r 48000 -t 0 -c "$conf_file" | tee "$log_file" &

    

    
  else
    # BPSK decode using csdr
    (
      echo "Starting BPSK decoding on device $i at ${freq} Hz..."| tee -a "$log_file"
      rtl_sdr -d $i -f $freq -s 960000 -g 30 - 2>>"$log_file" | \
        csdr convert_u8_f 2>>"$log_file" | \
        csdr fir_decimate_cc 40 2>>"$log_file" | \
        csdr fastagc_ff 2>>"$log_file" | \
        csdr bpsk_demod 2>>"$log_file" | \
        csdr binary_slicer_ff 2>>"$log_file" | \
        tee "$log_file"
        
    ) &
  fi
done






echo
echo "All decoders are now running. Logs are being written to:"
for ((i=0; i<device_count; i++)); do
  echo "  - /home/pi/CubeSatSim/groundstation/MTU_swarm_logs/device_${i}.log"
done
echo


#keeps the script running until all background processes end.
wait || echo "A background job exited unexpectedly."



