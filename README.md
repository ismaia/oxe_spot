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
sudo apt install python3-dbus python3-paho-mqtt python3-pip mosquitto mosquitto-clients pulseaudio pulseaudio-module-bluetooth
sudo pip3 install bluezero pulsectl 
```


### Installation (user space) 


`~/.config/systemd/user/pulseaudio.service`:

```
[Unit]
Description=Pulseaudio Sound Service
Requires=pulseaudio.socket

[Service]
Type=notify
ExecStart=/usr/bin/pulseaudio --verbose --daemonize=no
ExecStartPost=/usr/bin/pactl load-module module-alsa-sink
Restart=on-failure

[Install]
Also=pulseaudio.socket
WantedBy=default.target
```


`~/.config/systemd/user/pulseaudio.socket`:

```
[Unit]
Description=Pulseaudio Sound System

[Socket]
Priority=6
Backlog=5
ListenStream=%t/pulse/native

[Install]
WantedBy=sockets.target
```


`~/.config/systemd/user/oxe_spot.service`:

```
[Unit]
Description=Oxe Spot Daemon

[Service]
WorkingDirectory=/home/pi/oxe_spot
ExecStart=/home/pi/oxe_spot/scripts/oxe_spotd.sh

[Install]
WantedBy=default.target
```

make your user's systemd instance independent from your user's sessions:

```
sudo loginctl enable-linger $USER
```

activate services: 

```
systemctl --user daemon-reload
systemctl --user enable pulseaudio.service
systemctl --user enable pulseaudio.socket
systemctl --user enable oxe_spot.service
```


### MISC

Start services
```
pulseaudio --kill
systemctl --user daemon-reload
systemctl --user enable pulseaudio.service
systemctl --user enable pulseaudio.socket
systemctl --user start pulseaudio.service
systemctl --user status pulseaudio.{service,socket}
```

Showing logs on a running system:

```
journalctl -f --user-unit oxe_spot.service
journalctl -f --user-unit pulseaudio.service
```