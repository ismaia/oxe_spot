# OXE SPOT


### Pulseaudio via systemd --user

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

make your user's systemd instance independent from your user's sessions:

```
sudo loginctl enable-linger $USER
```

To start:

```
pulseaudio --kill
systemctl --user daemon-reload
systemctl --user enable pulseaudio.service
systemctl --user enable pulseaudio.socket
systemctl --user start pulseaudio.service
systemctl --user status pulseaudio.{service,socket}
```


## systemctl 

### Follow logs

```
journalctl -f --user-unit oxe_spot.service
journalctl -f --user-unit pulseaudio.service
```


