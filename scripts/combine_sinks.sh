#!/bin/bash
pactl list modules short
pactl load-module module-combine-sink adjust_time=5 resample_method=soxr-mq sink_name=combined_sinks slaves=alsa_output.pci-0000_00_1b.0.analog-stereo,bluez_sink.EC_81_93_A9_47_36.a2dp_sink
pactl set-default-sink combined_sinks
pactl list modules short



