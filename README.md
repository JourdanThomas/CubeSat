# CubeSat MTU
This project is the results of the work of five different interns, 3 in 2023 and 2 in 2025.

This project is divided into different stages. 
The first stage involved constructing a CubeSat using the information provided for the AMSAT CubeSatSim prototype, available at [CubeSatSim repository](https://github.com/alanbjohnston/CubeSatSim.git). We followed the steps outlined and replicated the foundation.
The second stage focused on enhancing the CubeSat in various ways to address a specific problem. 

1. **Real-time Visualization of CubeSat in Space using Gyroscope:**
   We developed a 3D visualization of our CubeSat in real-time on a website. This visualization updates dynamically as the ground station receives information.

2. **Prototyping CubeSat Maneuverability using Reaction Wheels:**
   We restructured the CubeSat to accommodate two motors and new electronic circuit components. This enhancement allows the CubeSat to orient itself in space based on reaction wheel principles.

3. **Decoding multiple CubeSats at the same time :**
   We created a new software to receive the RF signals from multiple CubeSats at the same time using different SDRs. The RF signal is then decoded and sent to the web server for data visualization.
   

For each of these separate projects, you'll find dedicated folders containing all the necessary information. Additionally, we undertook a thorough analysis of the base code available for CubeSatSim to interact effectively with our enhancements. We've added comments to certain sections of code in the 'soft' directory for the purpose of understanding. It's important to note that these commented code sections have not been altered; they serve merely as tools for comprehension.

## Folder Structure

- **CubeSat_Troubleshooting:** Contains details related to the construction phase following the AMSAT prototype and the solutions to different problems.
- **Visualisation_Improvement:** Includes resources for the real-time 3D visualization of the CubeSat.
- **Reaction_Wheel_Improvement:** Encompasses information regarding the CubeSat's ability to orient itself using reaction wheels.
- **Soft:** Holds the original base code with additional comments for understanding purposes.
- **Web_Serveur:** Contains all the files necessary to visualize various web pages related to the Cubesat, including the work done by other group members.
- **Swarm_decode**  Contains all the file to receive and decode RF signals from multiple CubeSats and how to display it on a web-server.
- **Module3_Camera_support**: Allows the CubeSat to support raspberry pi module 3 cameras such as a the NoIR cameras. By default it only supports module 2.
- **Distributed computing**: Work in progress for the development of a distributed computing network for image processing

Please refer to individual folders for specific details and resources related to each stage of the project.

## Important Note

The commented sections in the 'soft' directory serve as aids for understanding the base code and should not be modified. They are solely intended to facilitate comprehension.

## Contributors
- CASTELLANO Amélie (2023)
- ENAULT Fanny (2023)
- HUGUET Yann (2023)(https://github.com/Yannouille29) 
- JOURDAN Thomas (2025)(https://github.com/JourdanThomas)
- CHETOUANE M’hamed (2025)

Feel free to reach out to us for any inquiries or clarifications regarding this project.
