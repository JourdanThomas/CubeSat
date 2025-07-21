import socket
import threading
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
import time
import pyqrcode



################################################
#     Configuration of PC's IP address and port
################################################
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

pc_ip = get_local_ip()   # IP address of the Wi-Fi shared with the Raspberry Pi
pc_port = 8080

config_port=5000


ascii_art = """  ____      _          ____        _   ____  _
 / ___|   _| |__   ___/ ___|  __ _| |_/ ___|(_)_ __ ___
| |  | | | | '_ \ / _ \___ \ / _` | __\___ \| | '_ ` _ \\
| |__| |_| | |_) |  __/___) | (_| | |_ ___) | | | | | | |
\____\__,_|_.__/ \___|____/ \__,_|\__|____/|_|_| |_| |_|
\ \      / /__| |__    ___  ___ _ ____   _____ _ __
 \ \ /\ / / _ \ '_ \  / __|/ _ \ '__\ \ / / _ \ '__|
  \ V  V /  __/ |_) | \__ \  __/ |   \ V /  __/ |
   \_/\_/ \___|_.__/  |___/\___|_|    \_/ \___|_|
"""

print(ascii_art)




print ("")
print("the PC IP is:",pc_ip)





# Location of the text file where you want to save the data
output_file = '/Users/thomasjourdan/Mines/stage/MTU/CubeSat_MTU-main/Web_Serveur/data.txt'






qr = pyqrcode. create(content='http://'+str(pc_ip)+':'+str(pc_port) )
print(qr. terminal(module_color='white', background='black'))








app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
CORS(app, resources={r"/get_data": {"origins": "*"}})


################################################
#        Routes for different pages
################################################

@app.route('/')
#main page
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/Reaction_Wheels')
def reaction_wheels():
    return render_template('Reaction_Wheels.html')

@app.route('/Wifi_Communication')
def wifi_communication():
    return render_template('Wifi_Communication.html')

@app.route('/3D_Visualisation')
def d_visualisation():
    return render_template('3D_Visualisation.html')

@app.route('/Meteor_Detection')
def meteor_detection():
    return render_template('Meteor_Detection.html')

@app.route('/Youtube_Link_RW')
def youtube_link_rw():
    return render_template('Youtube_Link_RW.html')

@app.route('/Youtube_Link_3D')
def youtube_link_3d():
    return render_template('Youtube_Link_3D.html')

@app.route('/Youtube_Link_Meteor')
def youtube_link_meteor():
    return render_template('Youtube_Link_Meteor.html')

@app.route('/Youtube_Link_WIFI')
def youtube_link_wifi():
    return render_template('Youtube_Link_WIFI.html')

@app.route('/Project_Link_Meteor')
def project_link_meteor():
    return render_template('Project_Link_Meteor.html')

@app.route('/Project_Link_3D')
def project_link_3d():
    return render_template('Project_Link_3D.html')

@app.route('/Project_Link_RW')
def project_link_rW():
    return render_template('Project_Link_RW.html')

@app.route('/Project_Link_WIFI')
def project_link_wifi():
    return render_template('Project_Link_WIFI.html')




################################################################################################


# Create a route to retrieve the IP (useful to get the IP from another device)

@app.route('/get_ip', methods=['GET'])
def get_ip():
    return jsonify({"ip_port": str(pc_ip)+':'+str(pc_port)})




# Create a route to retrieve data
@app.route('/get_data', methods=['GET'])
def get_data():
    time.sleep(1)
    try:
        with open(output_file, 'r') as f:
            data = f.read().splitlines()
            str_data = []

            # If the file has more than 3 lines, take the last 3 lines
            if len(data) > 3:
                data = data[-3:]

            # Split each line using comma as a delimiter
            for d in data:
                values = d.split(',')
                # Add values to str_data
                str_data.append(values)

        return jsonify(str_data)
    
    except FileNotFoundError:
        error_message = f"Error: The file '{output_file}' can't be found."
        print(error_message)  # Log to console
        return jsonify({"error": f"The file '{output_file}' can't be found."}), 404 

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)  # Log to console
        return jsonify({"error": f"There has been an error : {str(e)}"}), 500


# Function to receive the config file from a socket
@app.route('/get_config', methods=['GET'])
def get_config():
    def receive_config():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((pc_ip, config_port))
        print(f"Config socket listening on {pc_ip}:{config_port}...")
        while True:
            data, addr = s.recvfrom(1024)
            received_data = data.decode('utf-8')
            print(f"[CONFIG] Received data from {addr}: {received_data}")
            with open(output_file, 'a') as f:
                f.write(received_data + '\n')
                print(f"[CONFIG] Data written to {output_file}")
    threading.Thread(target=receive_config, daemon=True).start()
    return jsonify({"status": f"Config receiver started on port {config_port}."})



@app.route('/get_alldata', methods=['GET'])
def get_alldata():
    def receive_alldata(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((pc_ip, port))
        print(f"[ALLDATA] Socket listening on {pc_ip}:{port}...")
        while True:
            data, addr = s.recvfrom(1024)
            received_data = data.decode('utf-8')
            print(f"[ALLDATA] Received data from {addr} on port {port}: {received_data}")
            with open(output_file, 'a') as f:
                f.write(received_data + '\n')
                print(f"[ALLDATA] Data written to {output_file}")

    # Start a thread for each port
    for port in alldata_ports:
        threading.Thread(target=receive_alldata, args=(port,), daemon=True).start()
    return jsonify({"status": f"All-data receivers started on ports {alldata_ports}."})





        

if __name__ == '__main__':
    # Create a thread to execute the receive_data function
    #receive_thread = threading.Thread(target=receive_data)

    # Start the thread
    #receive_thread.start()
    app.run(host='0.0.0.0', port=8080)  # Run the Flask server on all PC interfaces

