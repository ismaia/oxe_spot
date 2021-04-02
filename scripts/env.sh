alias pa-sinks='pactl list sinks short'
alias pa-srcs='pactl list sources short'
alias pa-mods='pactl list modules short'
alias pa-ldmd='pactl load-module'
alias vol-sc2='pactl set-sink-volume alsa_output.pci-0000_00_1b.0.analog-stereo'
alias vol-mb3='pactl set-sink-volume bluez_sink.EC_81_93_A9_47_36.a2dp_sink'

function vol() {
    v=$1
    pactl set-sink-volume alsa_output.pci-0000_00_1b.0.analog-stereo $v
    pactl set-sink-volume bluez_sink.EC_81_93_A9_47_36.a2dp_sink $v
}
