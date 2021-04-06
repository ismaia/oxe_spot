import logging
import sys
import dbus
import signal
import time
import paho.mqtt.client as mqtt

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


def mqtt_on_message(client, userdata, msg):
    logger.info('topic=%s, payload=%s' , msg.topic, str(msg.payload))


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

    #=============================================
    logger.info('Ready')
    mqtt_client.publish(MQTT_OXE_SPOT_TOPIC, payload='Ready')

    loop = GLib.MainLoop()
    loop.run()