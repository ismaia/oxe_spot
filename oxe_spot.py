import logging
import sys
import dbus
import signal
import time
import paho.mqtt.client as mqtt
import threading
import json

from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from bluetooth.bt_service import BtService
from audio.audio_service import AudioService

#=============================================
# MQTT TOPICS
#=============================================
MQTT_OXE_SPOT_TOPIC='/oxe_spot'
BT_SPK_STATUS_TOPIC=MQTT_OXE_SPOT_TOPIC+'/bt_spkr_status'
BT_SPK_CMD_TOPIC=MQTT_OXE_SPOT_TOPIC+'bt_spkr_cmd'

#=============================================
# Globals
#=============================================

logging.basicConfig(level=logging.DEBUG, format='%(name)s :: %(message)s')
logger = logging.getLogger(name='oxe_spot')
bt_service = BtService.instance()
audio_service = AudioService.instance()
conf_dict = {}


#=============================================

def signal_handler(sig, frame):
    logger.info('done')
    mqtt_client.publish(MQTT_OXE_SPOT_TOPIC+'/status', payload='Off')
    bt_service.stop()
    audio_service.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


#=============================================

def load_conf():  
    # Opening JSON file
    with open('conf/oxe_spot.json') as json_file:
        data = json.load(json_file)        
            
        msg = '['
        for conf in data:                        
            #format = '[["opt1","1"],["opt2","2"],["opt3","3"]]'            
            descr = data[conf]['description']
            name  = data[conf]['name']
            conf_dict[name] = data[conf] #build a dict with name as key
            msg   = msg + '["' + descr + '","' + name + '"],'
            logger.info('config name=%s descr=%s', name, descr)
        
        msg = msg[:-1] #remove the last comma
        msg = msg + ']'
        mqtt_client.publish(MQTT_OXE_SPOT_TOPIC+'/conf_load', payload=msg)
    


#=============================================
# BT Speakers
#=============================================
bt_spkr = None


def bt_speaker_send_connected_msg():
    mqtt_client.publish(BT_SPK_STATUS_TOPIC, payload='connected')

def bt_speaker_send_not_connected_msg():
    mqtt_client.publish(BT_SPK_STATUS_TOPIC, payload='not connected')

def bt_speaker_on_connect(dev):
    if dev == None:
        bt_speaker_send_not_connected_msg()
        return

    logger.info('Device connected : [ %s : %s ]' , dev.alias , dev.address )
    bt_speaker_send_connected_msg()
    audio_service.print_sinks()
    


def bt_speaker_on_disconnect(dev):
    if dev == None:
        bt_speaker_send_not_connected_msg()
        return    
    
    logger.info('Device disconnected : [ %s : %s ]' , dev.alias , dev.address )
    bt_speaker_send_not_connected_msg()
    audio_service.print_sinks()

def bt_speaker_check_connect_state(spk):
    if spk == None:
        bt_speaker_send_not_connected_msg()
        return

    time.sleep(4)
    if spk.connected:
        bt_speaker_send_connected_msg()
    else:
        bt_speaker_send_not_connected_msg()


def bt_speaker_on_message(topic, payload):        
    global bt_spkr

    if 'bt_command' in topic:
        logger.info('bt_command:%s', payload)
        if bt_spkr == None:
            mqtt_client.publish(BT_SPK_STATUS_TOPIC, payload='cant find speaker')
            return
        
        if payload == 'connect':
            mqtt_client.publish(BT_SPK_STATUS_TOPIC, payload='connecting...')
            logger.info('connecting [%s %s]', str(bt_spkr.address), str(bt_spkr.alias))                        
            bt_spkr.connect()
              
        elif payload == 'disconnect':
            mqtt_client.publish(BT_SPK_STATUS_TOPIC, payload='disconnecting...')
            logger.info('diconnecting [%s %s]', str(bt_spkr.address), str(bt_spkr.alias))            
            bt_spkr.disconnect()
        
        th = threading.Thread(target=bt_speaker_check_connect_state, args=(bt_spkr,))
        th.start()
            
    elif 'select_speaker' in topic:
        logger.info('select speaker:%s' , payload)
        bt_spkr = bt_service.get_device_by_name(payload, 'hci1') 
        



#=============================================
# MQTT callbacks
#=============================================

def mqtt_on_connect(client, userdata, flags, rc):
    logger.info("Connected to MQTT Broker")
    mqtt_client.subscribe(MQTT_OXE_SPOT_TOPIC + "/#")



def mqtt_on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    topic = msg.topic
    #logger.info('topic=%s, payload=%s' , topic, payload)
    if 'bt_spkr' in topic:
        bt_speaker_on_message(topic,payload)


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    #=============================================
    # MQTT 
    #=============================================
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect_async(host='localhost', port=1883, keepalive=60, bind_address="")
    mqtt_client.loop_start()


    #=============================================
    # load config 
    #=============================================

    load_conf()


    #=============================================
    # Bluetooth
    #=============================================
    hci0_dev='hci0'
    hci1_dev='hci1'    
    hci0_alias='oxe_spot'
    hci1_alias='a2dp_port'
    hci0 = None
    hci1 = None
    
    bt_service.adapter_on(hci0_dev)
    bt_service.adapter_set_class(hci_index=0, major='0x04', minor='0x02')
    bt_service.adapter_on(hci1_dev)
    bt_service.adapter_set_alias(hci0_dev, hci0_alias)
    bt_service.adapter_set_alias(hci1_dev, hci1_alias)
    bt_service.adapter_set_discoverable(hci0_dev)  
    hci0 = bt_service.adapter_get_instance(hci0_dev)
    hci1 = bt_service.adapter_get_instance(hci1_dev)
    hci1.on_connect = bt_speaker_on_connect
    hci1.on_disconnect = bt_speaker_on_disconnect


    bt_spkr = bt_service.get_device_by_name('MEGABOOM 3', hci1_dev) #default speaker
    bt_speaker_check_connect_state(bt_spkr)


    #=============================================
    # Pulseaudio
    #=============================================
    audio_service.print_sources()
    audio_service.print_sinks()

    #=============================================
    logger.info('ready')
    mqtt_client.publish(MQTT_OXE_SPOT_TOPIC+'/status', payload='ready')

    loop = GLib.MainLoop()
    loop.run()