#!/bin/bash
pactl load-module module-combine-sink adjust_time=4 resample_method=soxr-mq sink_name=combined_sinks slaves=alsa_output.pci-0000_00_1b.0.analog-stereo,bluez_sink.EC_81_93_A9_47_36.a2dp_sink
sleep 1
pactl load-module module-null-sink
sleep 1
pactl load-module module-null-source
sleep 1
pactl set-default-sink null
pactl set-default-source source.null
pactl load-module module-loopback source=alsa_input.usb-0d8c_USB_Sound_Device-00.analog-stereo sink=combined_sinks

