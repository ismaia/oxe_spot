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
   mosquitto_pub -t "/oxe/home/status" -m "Off"
   cleanup_subprocs   
   exit
}

cleanup_subprocs
echo "OXE watchdog"
mosquitto_sub -t "/oxe/app" > "$MAIN_PIPE" & 

function start_oxe_spot() {
    if [ "$oxe_pid" == "" ]; then
       kill -SIGINT $oxe_pid &>/dev/null           
       echo "starting oxe_spot..."
       /usr/bin/python3 $HOME/oxe_spot/oxe_spot.py &
       oxe_pid=$!
       if [ ! -z $oxe_pid ]; then 
        mosquitto_pub -t "/oxe/home/status" -m "ready"
        mosquitto_pub -t "/oxe/home/status" -m "ready"
       fi
    else        
       echo "oxe_spot already running!"
    fi
}


function stop_oxe_spot() {
    mosquitto_pub -t "/oxe/home/status" -m "Off"
    if [ ! -z $oxe_pid ]; then 
       echo "killing pid=$oxe_pid"
       kill -SIGINT $oxe_pid
       oxe_pid=""
    fi
}


function main_loop()
{
    while read cmd <$MAIN_PIPE ; 
    do    
        echo "cmd : $cmd"
        case "$cmd" in
        "start"*)
            echo "exec start"
            start_oxe_spot
            ;;
        "stop"*)
            echo "exec stop"
            stop_oxe_spot
            ;;
        "reboot"*)
            echo "exec reboot"
            sudo systemctl reboot
            ;;
        "suspend"*)
            echo "exec suspend"
            sudo systemctl suspend
            ;;
    
        "poweroff"*)
            echo "exec poweroff"
            sudo systemctl poweroff
            ;;
        esac
    done
}

#######################################
start_oxe_spot
main_loop



