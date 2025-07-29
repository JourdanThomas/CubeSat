# Distributed computing network for image processing
On a small satellite such as a cubesat, the computing power of a single cubesat might be limited. This is why it can be interesting to create a distributed computing network between the different cubesat when more computing power is needed.
Distributed Satellite System (DSS) architectures


We will be implementing a star architecture with a central hub that can be placed on a cubesat that will act as a master
# Communication






# Setting up the Program

## on the Master
We will be using the network manager and scapy, if it is the first time starting the program you will need:
```
sudo apt update
sudo apt install network-manager
sudo apt install python3-scapy -y
```
You can then detect device via

nmcli device

















### Sources

Distributed Computing on CubeSat Clusters using MapReduce
Obulapathi N Challa, Dr. Janise McNair
University of FLorida
https://icubesat.org/wp-content/uploads/2012/06/icubesat-org-2012-a-2-6-_paper_challa.pdf



A Distributed Computing Architecture for Small Satellite
and Multi-Spacecraft Missions
Bryan Palmintier∗ , Christopher Kitts∗ , Pascal Stang∗ and Michael Swartwout∗∗
∗ Robotic Systems Laboratory, Santa Clara University, Santa Clara CA 95053
∗∗Department of Mechanical Engineering, Washington University in St. Louis, St. Louis MO 63130
https://digitalcommons.usu.edu/cgi/viewcontent.cgi?referer=&httpsredir=1&article=1916&context=smallsat