# coding=utf-8
import socket
import time
import logging

logging.basicConfig(filename='/home/pi/CubeSatSim/sender2.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Configuration de l'adresse IP et du port du serveur Flask
server_ip = '172.20.10.5'  # Remplacez ceci par l'adresse IP de votre serveur Flask
server_port = 8080

# Emplacement du fichier .log
log_file = '/home/pi/FoxTelemetryData-CubeSatSim/FOXDB/FOX7rttelemetry_35_104.log' # Bien adapter au nouveau fichier payload

# Créer une socket pour la communication
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
previous_line = ""

while True:
	with open(log_file, 'r') as f:
		lines = f.readlines()

	    	# Obtenir la dernière ligne du fichier
		last_line = lines[-1].strip()
	    
	    	# Vérifier si la ligne a changé pour éviter l'envoi de doublons
		if previous_line != last_line:
			# Envoyer la dernière ligne au serveur Flask
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
