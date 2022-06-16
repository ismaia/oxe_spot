## Oxe Spot

My personal home automation system
  * Devices
    * 2x BT speakers (Audio sinks)
    * A Turntable (Audio Source)
    * SmartPhone (Audio Source)    

  * App
    * python backend 
    * Node-RED (UI)
  
All communication between backend<->frontend is made by MQTT message passing

### Install Dependencies 
```
sudo apt install python3-dbus python3-paho-mqtt mosquitto python3-pip
sudo pip3 install bluezero pulsectl 
```
