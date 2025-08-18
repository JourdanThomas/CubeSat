# How to setup the web server on the virtual machine


# First install

## Connect via SSH
You should be connected to the same network as the hosting machine
Connect via SSH to the web server using the following command:
```bash
ssh -p 40022 cubesatlab@172.31.1.13 
```

## copy the GitHub repository to the web server

Here is the link to the GitHub repository:
https://github.com/JourdanThomas/CubeSat/tree/main/Swarm_decode/Web_Serveur

You can clone the repository by running the following command:
```
git clone https://github.com/JourdanThomas/CubeSat.git
```

Then navigate into the subdirectory:
```
cd CubeSat/Swarm_decode/Web_Serveur

```

## install Python and Packages
### Python
You should install Python:

```
sudo apt update
sudo apt install python3 -y
```

### Packages
The install the packages necessary for the web server:
```
pip install flask flask-cors pyqrcode
```
Or you can use the following command if the other one doesn’t work:	
```
pip3 install flask flask-cors pyqrcode
```
Or if it doesn’t work, you can use the following command:(works on ubuntu)
```
sudo apt install python3-flask python3-flask-cors python3-pyqrcode -y
```


## Running the web server
```
python3 CubeSat/Swarm_decode/Web_Serveur/pc.py
```

# Maintenance
## How to update the webserver
Manually pull updates
```bash
cd ~/CubeSat
git pull origin main
cd ..

```
Update automatically using a cron job

crontab -e

For an update every hour, add the following line:
```bash
0 * * * * cd /home/cubesatlab/CubeSat && git pull origin main
```
For an update every 10 minutes, add the following line:
```bash
*/10 * * * * cd /home/cubesatlab/CubeSat && git pull origin main
```
For an update every day (at 2am), add the following line:
```bash
0 2 * * * cd /home/cubesatlab/CubeSat && git pull origin main
```



## Launch at startup
Edit crontab:
```
crontab -e
```
Add the line to launch the web server at startup:
```
@reboot cd /home/cubesatlab/CubeSat/Swarm_decode/Web_Serveur && nohup python3 app.py &
```
- @reboot → runs the script at machine startup.
- nohup → allows it to keep running after logout.
- & → runs it in the background.

## Automatically stop and restart the web server









