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


MAIN_STATUS_T='/oxe/main/status'

#=============================================
# Globals
#=============================================

logging.basicConfig(level=logging.DEBUG, format='%(name)s :: %(message)s')
logger = logging.getLogger(name='oxe_spot')

bt_service = BtService.instance()
audio_service = AudioService.instance()


#=============================================
# MQTT 
#=============================================

class MqttClient:
    __instance = None
    @staticmethod 
    def instance():
        """ Static access method. """
        if MqttClient.__instance == None:
            MqttClient()
        return MqttClient.__instance

    def __init__(self):
        if MqttClient.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MqttClient.__instance = self
        self.mqtt_cli = None
        self.dispatch_dict = {}

    def start(self):
        self.mqtt_cli = mqtt.Client()
        self.mqtt_cli.on_connect = self.on_connect
        self.mqtt_cli.on_message = self.on_message
        self.mqtt_cli.connect_async(host='localhost', port=1883, keepalive=60, bind_address="")
        self.mqtt_cli.loop_start()

    def pub(self,topic, payload):
        self.mqtt_cli.publish(topic, payload)

    def on_connect(self,client, userdata, flags, rc):
        logger.info("Connected to MQTT Broker")
        self.mqtt_cli.subscribe("/oxe/#")

    def add_msg_handler(self, topic, callback):
        self.dispatch_dict[topic] = callback

    def on_message(self,client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic    
        
        if topic in self.dispatch_dict:
            callback = self.dispatch_dict[topic]
            callback(topic,payload)
    
mqtt_cli = MqttClient.instance()


#=============================================
# Signal Handler  : SIGINT
#=============================================

def signal_handler(sig, frame):
    logger.info('done')
    mqtt_cli.pub(MAIN_STATUS_T, payload='Off')
    bt_service.stop()
    audio_service.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)



#=============================================
# Main
#=============================================
class OxeSpotMain:
    __instance = None
    @staticmethod 
    def instance():
        """ Static access method. """
        if OxeSpotMain.__instance == None:
            OxeSpotMain()
        return OxeSpotMain.__instance

    def __init__(self):
        if OxeSpotMain.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            OxeSpotMain.__instance = self
        self.conf_dict = {}
        self.conf_list_topic = '/oxe/main/conf/list'


    def start(self):
        self._load_conf()

    def _load_conf(self):  
        # Opening JSON file
        with open('conf/oxe_spot.json') as json_file:
            data = json.load(json_file)                        
        msg = '['
        for conf in data:                        
            #format = '[["opt1","1"],["opt2","2"],["opt3","3"]]'            
            descr = data[conf]['description']
            name  = data[conf]['name']
            self.conf_dict[name] = data[conf] #build a dict with name as key
            msg   = msg + '["' + descr + '","' + name + '"],'
            logger.info('config name=%s descr=%s', name, descr)
        
        msg = msg[:-1] #remove the last comma
        msg = msg + ']'
        mqtt_cli.pub(self.conf_list_topic, payload=msg)
    
    def on_msg_conf_select(self,topic,payload):
        logger.info('on_msg_conf_select %s', payload)

    def on_msg_vol_ctrl1_mute(self,topic,payload):
        logger.info('on_msg_vol_ctrl1_mute %s', payload)

    def on_msg_vol_ctrl1_vol(self,topic,payload):
        logger.info('on_msg_vol_ctrl1_vol %s', payload)

    def on_msg_vol_ctrl2_mute(self,topic,payload):
        logger.info('on_msg_vol_ctrl2_mute %s', payload)

    def on_msg_vol_ctrl2_vol(self,topic,payload):
        logger.info('on_msg_vol_ctrl2_vol %s', payload)


oxe_spot = OxeSpotMain.instance()

#=============================================
# Audio Controls
#=============================================

class AudioCtl:
    __instance = None
    @staticmethod 
    def instance():
        """ Static access method. """
        if AudioCtl.__instance == None:
            AudioCtl()
        return AudioCtl.__instance

    def __init__(self):
        if AudioCtl.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            AudioCtl.__instance = self
        
        self.audio_port = ''
                


audio_ctl = AudioCtl.instance()

#=============================================
# BT Speaker
#=============================================

class BtSpeaker:
    __instance = None
    @staticmethod 
    def instance():
        """ Static access method. """
        if BtSpeaker.__instance == None:
            BtSpeaker()
        return BtSpeaker.__instance

    def __init__(self):
        if BtSpeaker.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            BtSpeaker.__instance = self
        
        self.bt_spkr_dev = None #Device object
        self.status_topic  = '/oxe/bt_spkr/status'
        self.bt_spkr_list = '/oxe/bt_spkr/list'        
    
    def load_conf(self):  
        # Opening JSON file
        with open('conf/oxe_spot.json') as json_file:
            data = json.load(json_file)        
            
        spkr_dict={}
        for conf in data:                        
            #format = '[["opt1","1"],["opt2","2"],["opt3","3"]]'
            conf_dict = data[conf]
            if 'audio_sink1_type' in conf_dict and conf_dict['audio_sink1_type'] == 'bt':
                s_descr = conf_dict['audio_sink1_descr']
                s_name  = conf_dict['audio_sink1_name']
                spkr_dict[s_descr] = s_name
                
            if 'audio_sink2_type' in conf_dict and conf_dict['audio_sink2_type'] == 'bt':
                s_descr = conf_dict['audio_sink2_descr']
                s_name  = conf_dict['audio_sink2_name']
                spkr_dict[s_descr] = s_name

        msg = '['
        for sp in spkr_dict:
            descr = sp
            name  = spkr_dict[sp]
            msg = msg + '["' + descr + '","' + name + '"],'
        msg = msg[:-1] #remove the last comma
        msg = msg + ']'             
        logger.info('BT speakers: %s' , msg)
        mqtt_cli.pub(self.bt_spkr_list, payload=msg)


    def send_msg_connected(self):
        mqtt_cli.pub(self.status_topic, payload='connected')

    def send_msg_not_connected(self):
        mqtt_cli.pub(self.status_topic, payload='not connected')

    def on_connect(self,dev):
        if dev == None:
            self.send_msg_not_connected()
            return
        logger.info('Device connected : [ %s : %s ]' , dev.alias , dev.address )
        self.send_msg_connected()

    def on_disconnect(self,dev):
        if dev == None:
            self.send_msg_not_connected()
            return    
        logger.info('Device disconnected : [ %s : %s ]' , dev.alias , dev.address )
        self.send_msg_not_connected()


    def check_connect_state(self,spk):
        if spk == None:
            self.send_msg_not_connected()
            return        
        if spk.connected:
            self.send_msg_connected()
        else:
            self.send_msg_not_connected()


    def on_msg_select(self,topic, payload):
        pass
    
    def on_msg_connect(self,topic, payload):
        if self.bt_spkr_dev == None:
            self.send_msg_not_connected()
            return
        mqtt_cli.pub(self.status_topic, payload='connecting...')
        logger.info('connecting [%s %s]', self.bt_spkr_dev.address, self.bt_spkr_dev.alias)
        self.bt_spkr_dev.connect()
        

    def on_msg_disconnect(self,topic, payload):
        if self.bt_spkr_dev == None:
            self.send_msg_not_connected()
            return
        mqtt_cli.pub(self.status_topic, payload='disconnecting...')
        logger.info('disconnecting [%s %s]', self.bt_spkr_dev.address, self.bt_spkr_dev.alias)
        self.bt_spkr_dev.disconnect()


    # th = threading.Thread(target=self.check_connect_state, args=(self.bt_spkr_dev,))
    # th.start()
            
bt_spkr = BtSpeaker.instance()


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    mqtt_cli.start()
    oxe_spot.start()
    bt_spkr.load_conf()

    #=============================================
    # Callback registration
    #=============================================
    mqtt_cli.add_msg_handler('/oxe/main/conf/select', oxe_spot.on_msg_conf_select)
    mqtt_cli.add_msg_handler('/oxe/main/vol_ctrl1/mute', oxe_spot.on_msg_vol_ctrl1_mute)
    mqtt_cli.add_msg_handler('/oxe/main/vol_ctrl1/vol', oxe_spot.on_msg_vol_ctrl1_vol)
    mqtt_cli.add_msg_handler('/oxe/main/vol_ctrl2/mute', oxe_spot.on_msg_vol_ctrl2_mute)
    mqtt_cli.add_msg_handler('/oxe/main/vol_ctrl2/vol', oxe_spot.on_msg_vol_ctrl2_vol)

    mqtt_cli.add_msg_handler('/oxe/bt_spkr/select', bt_spkr.on_msg_select)
    mqtt_cli.add_msg_handler('/oxe/bt_spkr/connect',bt_spkr.on_msg_connect)
    mqtt_cli.add_msg_handler('/oxe/bt_spkr/disconnect',bt_spkr.on_msg_disconnect)



    

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
    hci1.on_connect = BtSpeaker.instance().on_connect
    hci1.on_disconnect = BtSpeaker.instance().on_disconnect


    #=============================================
    # Audio
    #=============================================
    audio_service.print_sources()
    audio_service.print_sinks()

    
    #=============================================
    logger.info('ready')
    mqtt_cli.pub(MAIN_STATUS_T, payload='ready')

    loop = GLib.MainLoop()
    loop.run()