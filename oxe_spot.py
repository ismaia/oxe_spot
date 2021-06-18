import logging
import sys
import dbus
import signal
import time
import paho.mqtt.client as mqtt
import threading
import json
import os, sys, traceback
import subprocess
import pulsectl

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

    def init(self):
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
    oxe_spot.destroy_audio_conf()
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
        self.curr_conf = None
        self.curr_source = None
        self.curr_sink1 = None
        self.curr_sink2 = None
        self.pa_module_list = []


    def init(self):
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
        logger.info('on_msg_conf_select conf=%s', payload)
        conf_name = payload
        sink1='-'
        sink2='-'
        if 'description' in self.conf_dict[conf_name]:
            self.curr_conf = self.conf_dict[conf_name]
        else:
            logger.info('Error on selecting config')
            return        
        
        if 'audio_sink1_descr' in self.curr_conf:
            sink1=self.curr_conf['audio_sink1_descr']

        if 'audio_sink2_descr' in self.curr_conf:
            sink2=self.curr_conf['audio_sink2_descr']                            

        mqtt_cli.pub('/oxe/main/vol_ctrl1/device_name', sink1)
        mqtt_cli.pub('/oxe/main/vol_ctrl2/device_name', sink2)
        mqtt_cli.pub('/oxe/main/notification', 'selected config :'+conf_name)
        self.build_audio_conf()
    
    def build_audio_conf(self):                
        try:
            self.destroy_audio_conf() #destroy previous audio conf
            
            pa = audio_service.pulse

            #null source
            m_idx = pa.module_load('module-null-source')    
            self.pa_module_list.append(m_idx)
            null_source=pa.get_source_by_name('source.null')
            pa.source_default_set(null_source)

            #null sink
            m_idx = pa.module_load('module-null-sink')    
            self.pa_module_list.append(m_idx)
            null_sink=pa.get_sink_by_name('null')
            pa.sink_default_set(null_sink)

            source1_name = self.curr_conf['audio_source1_name']
            self.curr_source = pa.get_source_by_name(source1_name)
            sink1_name = self.curr_conf['audio_sink1_name']
            self.curr_sink1 = pa.get_sink_by_name(sink1_name)

            if self.curr_conf['sink_type'] == 'combined':
                sink2_name = self.curr_conf['audio_sink2_name']
                self.curr_sink2 = pa.get_sink_by_name(sink2_name)
                m_idx = pa.module_load('module-combine-sink', 'adjust_time=5 sink_name=combined_sinks slaves='+sink1_name+','+sink2_name)
                self.pa_module_list.append(m_idx)
                m_idx = pa.module_load('module-loopback', 'source='+source1_name + ' sink=combined_sinks')
                self.pa_module_list.append(m_idx)
            elif self.curr_conf['sink_type'] == 'single':
                m_idx = pa.module_load('module-loopback', 'source='+source1_name + ' sink='+sink1_name)
                self.pa_module_list.append(m_idx)
        except:
            mqtt_cli.pub('/oxe/main/notification', 'Error on creating pa module')
            self.destroy_audio_conf()
            self._log_exception()


    def destroy_audio_conf(self):
        try:
            pa = audio_service.pulse
            for i in self.pa_module_list:
                pa.module_unload(i)
            self.pa_module_list.clear()
        except:
            mqtt_cli.pub('/oxe/main/notification', 'Error on removing pa module')
            self._log_exception()


    def on_msg_vol_ctrl1_mute(self,topic,payload):
        logger.info('on_msg_vol_ctrl1_mute %s', payload)

    def on_msg_vol_ctrl1_vol(self,topic,payload):
        logger.info('on_msg_vol_ctrl1_vol %s', payload)

    def on_msg_vol_ctrl2_mute(self,topic,payload):
        logger.info('on_msg_vol_ctrl2_mute %s', payload)

    def on_msg_vol_ctrl2_vol(self,topic,payload):
        logger.info('on_msg_vol_ctrl2_vol %s', payload)

    def _log_exception(self):
        ex = str(sys.exc_info()[1])
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)
        func_name = stk[0][2]            
        logger.error("Error : " + func_name + ' : ' + ex)


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
        self.status_topic = '/oxe/bt_spkr/status'
        self.bt_spkr_list = '/oxe/bt_spkr/list'       
        self.default_hci  = 'hci1'         

    def init(self):
        self.load_conf()
        mqtt_cli.pub(bt_spkr.status_topic, '-')

    
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
                spkr_dict[s_descr] = s_descr #key = value
                
            if 'audio_sink2_type' in conf_dict and conf_dict['audio_sink2_type'] == 'bt':
                s_descr = conf_dict['audio_sink2_descr']                
                spkr_dict[s_descr] = s_descr #key = value

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

    def send_msg_select_spkr(self):
        mqtt_cli.pub(self.status_topic, payload='select a speaker')
    

    def on_connect(self,dev):
        if dev == None:
            self.send_msg_select_spkr()
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
            self.send_msg_select_spkr()
            return        
        if spk.connected:
            self.send_msg_connected()
        else:
            self.send_msg_not_connected()


    def on_msg_select(self,topic, payload):
        self.bt_spkr_dev = bt_service.get_device_by_name(payload,self.default_hci)
        if self.bt_spkr_dev == None:
            mqtt_cli.pub(self.status_topic, payload='Not available')
            mqtt_cli.pub('/oxe/bt_spkr/notification','Speaker not available or not paired')

    
    def on_msg_connect(self,topic, payload):
        try:
            if self.bt_spkr_dev == None:
                self.send_msg_select_spkr()
                return
            if self.bt_spkr_dev.connected:
                self.send_msg_connected()
                logger.info('[%s %s] already connected', self.bt_spkr_dev.address, self.bt_spkr_dev.alias)
                return

            mqtt_cli.pub(self.status_topic, payload='connecting...')
            logger.info('connecting [%s %s]', self.bt_spkr_dev.address, self.bt_spkr_dev.alias)
            self.bt_spkr_dev.connect()
        except:
            self.send_msg_not_connected()
            self._log_exception()
        

    def on_msg_disconnect(self,topic, payload):
        try:        
            if self.bt_spkr_dev == None:
                self.send_msg_select_spkr()
                return
            mqtt_cli.pub(self.status_topic, payload='disconnecting...')
            logger.info('disconnecting [%s %s]', self.bt_spkr_dev.address, self.bt_spkr_dev.alias)
            self.bt_spkr_dev.disconnect()
        except:
            self.send_msg_not_connected()
            self._log_exception()

    def _log_exception(self):
        ex = str(sys.exc_info()[1])
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)
        func_name = stk[0][2]            
        logger.error("Error : " + func_name + ' : ' + ex)

            
bt_spkr = BtSpeaker.instance()


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    mqtt_cli.init()
    oxe_spot.init()
    bt_spkr.init()

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

    #pa = audio_service.pulse


    loop = GLib.MainLoop()
    loop.run()