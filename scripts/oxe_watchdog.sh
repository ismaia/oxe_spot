#!/bin/bash

MAIN_PIPE="/tmp/oxe_spot"

trap "rm -f $MAIN_PIPE" exit

if [[ ! -p $MAIN_PIPE ]]; then
  mkfifo $MAIN_PIPE
fi


oxe_pid=""

function cleanup_subprocs() {
  kill $(jobs -p) &> /dev/null
  #kill all instances of this script except myself
  script_name=${BASH_SOURCE[0]}
  for pid in $(pidof -x $script_name); do
      if [ $pid != $$ ]; then
        kill -9 $pid &>/dev/null
      fi
  done
  kill -SIGINT $oxe_pid &>/dev/null  
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
mosquitto_pub -t "/oxe/home/status" -m "Off"

while true
do
if read cmd <$MAIN_PIPE; 
then      
    echo "cmd : $cmd"
    case "$cmd" in
    "start"*)
        echo "received start cmd"
        if [ "$oxe_pid" == "" ]; then
           kill -SIGINT $oxe_pid &>/dev/null
           mosquitto_pub -t "/oxe/app" -m "stop"           
           echo "starting oxe_spot..."
           /usr/bin/python3 /home/isaac/oxe_spot_snap/oxe_spot.py &
           oxe_pid=$!
        else        
           echo "oxe_spot already running!"
        fi
        ;;
    "stop"*)
        echo "received stop cmd"
        mosquitto_pub -t "/oxe/app" -m "stop"
        mosquitto_pub -t "/oxe/home/status" -m "Off"
        oxe_pid=""
        ;;
    "reboot"*)
        echo "received reboot cmd"
        sudo systemctl reboot
        ;;
    "suspend"*)
        echo "received suspend cmd"
        sudo systemctl suspend
        ;;

    "poweroff"*)
        echo "received poweroff cmd"
        sudo systemctl poweroff
        ;;
    esac
fi
done
