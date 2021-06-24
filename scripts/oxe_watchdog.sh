#!/bin/bash

MAIN_PIPE="/tmp/oxe_spot"

trap "rm -f $MAIN_PIPE" exit

if [[ ! -p $MAIN_PIPE ]]; then
  mkfifo $MAIN_PIPE
fi

function cleanup_subprocs() {
  kill $(jobs -p) &> /dev/null
  #kill all instances of this script except myself
  script_name=${BASH_SOURCE[0]}
  for pid in $(pidof -x $script_name); do
      if [ $pid != $$ ]; then
        kill -9 $pid &>/dev/null
      fi
  done
}


# trap ctrl-c and call ctrl_c()
trap ctrl_c INT
function ctrl_c() {
   echo "Terminating..."
   cleanup_subprocs   
   exit
}

cleanup_subprocs
echo "OXE watchdog"
mosquitto_sub -t "/oxe/app" > "$MAIN_PIPE" & 

while true
do
if read cmd <$MAIN_PIPE; 
then      
    echo "cmd : $cmd"
    case "$cmd" in
    "start"*)
        echo "received start cmd"
        mosquitto_pub -t "/oxe/app" -m "stop"
        sleep 1
        /usr/bin/python3 /home/isaac/oxe_spot_snap/oxe_spot.py &
        ;;
    "stop"*)
        echo "received stop cmd"
        mosquitto_pub -t "/oxe/app" -m "stop"
        ;;
    "reboot"*)
        echo "received reboot cmd"
        sudo reboot
        ;;
    "poweroff"*)
        echo "received poweroff cmd"
        sudo poweroff
        ;;
    esac
fi
done
