# coding=utf-8

#######################################################
# MTU            Swarm_packet_transmit.py
# script to auto decode packet using rtl_fm and Direwolf
# made by Thomas Jourdan
# 07/2025
#######################################################



import socket
import time
import logging

logging.basicConfig(filename='/home/pi/CubeSatSim/sender3.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Configuration de l'adresse IP et du port du serveur Flask
server_ip = '172.20.10.5'  # Remplacez ceci par l'adresse IP de votre serveur Flask
server_port = 8080

with open('/home/pi/CubeSatSim/groundstation/MTU_swarm_logs/MTU_config.txt') as f:
    cfg = dict(line.strip().split('=') for line in f)
    host_ip = cfg['Host_IP']
    device_count = int(cfg['Device_Count'])
    freqs = list(map(int, cfg['Frequencies'].split()))
    print(host_ip, device_count, freqs)



# Emplacement du fichier .log
log_file = '/home/pi/FoxTelemetryData-CubeSatSim/FOXDB/FOX7rttelemetry_35_104.log' # Bien adapter au nouveau fichier payload

# Créer une socket pour la communication
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
previous_line = ""

while True:
	with open(log_file, 'r') as f:
		lines = f.readlines()

	    # Getting the last line of the file
		last_line = lines[-1].strip()
	    
	    #check if the line changed
		if previous_line != last_line:
			#send the last one to the flask server
			message = last_line
			s.sendto(message.encode('utf-8'), (server_ip, server_port))
			logging.info(f"Sent: {message}")
			previous_line = last_line  # Mettre à jour la ligne précédente


		#else:
		#	message="The file is not updated"
		#	s.sendto(message.encode('utf-8'), (server_ip, server_port))
		#	logging.info(f"Sent: {message}")
		#	time.sleep(5)
		time.sleep(3)  # Attendre 3 secondes avant de vérifier à nouveau le fichier
