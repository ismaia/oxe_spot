#!/bin/bash
pactl load-module module-null-sink sink_name=sink1
pactl load-module module-null-sink sink_name=sink2
#pactl load-module module-combine-sink adjust_time=4 resample_method=soxr-mq sink_name=combined_sinks slaves=sink1,sink2
pactl load-module module-combine-sink adjust_time=5 resample_method=soxr-mq sink_name=combined_sinks slaves=sink1,sink2
pactl load-module module-loopback source=sink1.monitor sink=bluez_sink.EC_81_93_A9_47_36.a2dp_sink
pactl load-module module-loopback source=sink2.monitor sink=alsa_output.pci-0000_00_1b.0.analog-stereo
pactl set-default-sink combined_sinks
pactl list modules short

