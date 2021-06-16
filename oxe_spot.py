import logging
import sys
import dbus
import signal
import time
import paho.mqtt.client as mqtt
import threading

from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from bluetooth.bt_service import BtService
from audio.audio_service import AudioService


logging.basicConfig(level=logging.DEBUG, format='%(name)s :: %(message)s')
logger = logging.getLogger(name='oxe_spot')
bt_service = BtService.instance()
audio_service = AudioService.instance()

def signal_handler(sig, frame):
    logger.info('done')
    bt_service.stop()
    audio_service.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

MQTT_OXE_SPOT_TOPIC='/oxe_spot'


def mqtt_on_connect(client, userdata, flags, rc):
    logger.info("Connected to MQTT Broker")
    mqtt_client.subscribe(MQTT_OXE_SPOT_TOPIC + "/#")



def on_bt_speaker_connect():
    logger.info('connected')
    mqtt_client.publish("/oxe_spot/bt_speakers/status", payload='connected')

def on_bt_speaker_disconnect():
    logger.info('not connected')
    mqtt_client.publish("/oxe_spot/bt_speakers/status", payload='not connected')

def check_connect_state(spk):    
    if spk == None:
        mqtt_client.publish("/oxe_spot/bt_speakers/status", payload='not connected')
        return
    time.sleep(4)
    logger.info('checking connection state')
    if spk.connected:
        mqtt_client.publish("/oxe_spot/bt_speakers/status", payload='connected')
    else:
        mqtt_client.publish("/oxe_spot/bt_speakers/status", payload='not connected')


def on_bt_speakers_message(topic, payload):        
    global bt_spkr

    if 'bt_command' in topic:
        logger.info('bt_command:%s', payload)
        if bt_spkr == None:
            mqtt_client.publish("/oxe_spot/bt_speakers/status", payload='cant find speaker')
            return            
        
        if payload == 'connect':
            mqtt_client.publish("/oxe_spot/bt_speakers/status", payload='connecting...')
            logger.info('connecting [%s %s]', str(bt_spkr.address), str(bt_spkr.alias))                        
            bt_spkr.connect()                
              
        elif payload == 'disconnect':
            mqtt_client.publish("/oxe_spot/bt_speakers/status", payload='disconnecting...') 
            logger.info('diconnecting [%s %s]', str(bt_spkr.address), str(bt_spkr.alias))            
            bt_spkr.disconnect()
        
        th = threading.Thread(target=check_connect_state, args=(bt_spkr,))
        th.start()
            
    elif 'select_speaker' in topic:
        bt_spkr = bt_service.get_device_by_name(payload, 'hci1') 
        logger.info('select speaker:%s' , payload)



def mqtt_on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    topic = msg.topic
    logger.info('topic=%s, payload=%s' , topic, payload)            
    if 'bt_speakers' in topic:
        on_bt_speakers_message(topic,payload)


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
    # Bluetooth
    #=============================================
    hci0='hci0'
    hci1='hci1'
    
    hci0_name='oxe_spot'
    hci1_name='a2dp_port1'    
    
    bt_service.adapter_on(hci0)
    bt_service.adapter_set_class(hci_index=0, major='0x04', minor='0x02')
    bt_service.adapter_on(hci1)
    bt_service.adapter_set_alias(hci0, hci0_name)    
    bt_service.adapter_set_alias(hci1, hci1_name)    
    bt_service.adapter_set_discoverable(hci0)  
    bt_service.set_on_connect_callback(hci1, on_bt_speaker_connect)
    bt_service.set_on_diconnect_callback(hci1, on_bt_speaker_disconnect)    
    bt_spkr = bt_service.get_device_by_name('MEGABOOM 3', 'hci1') #default speaker
    check_connect_state(bt_spkr)


    #=============================================
    logger.info('Ready')
    mqtt_client.publish(MQTT_OXE_SPOT_TOPIC, payload='Ready')

    loop = GLib.MainLoop()
    loop.run()