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


#=============================================
# Globals
#=============================================

#working dir
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


logging.basicConfig(level=logging.DEBUG, format='%(name)s :: %(message)s')
logger = logging.getLogger(name='oxe_spot')

bt_service = None
mqtt_cli = None
home_vw = None
audio_ctl_vw = None
pa = None
bt_spkr_vw = None
oxe_spot = None

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
        self.ready = False

    def init(self):
        self.mqtt_cli = mqtt.Client()
        self.mqtt_cli.on_connect = self.on_connect
        self.mqtt_cli.on_message = self.on_message
        self.mqtt_cli.connect_async(host='localhost', port=1883, keepalive=60, bind_address="")
        self.mqtt_cli.loop_start()
        while not self.ready:
            time.sleep(0.3)

    def pub(self,topic, payload):
        self.mqtt_cli.publish(topic, payload)

    def on_connect(self,client, userdata, flags, rc):
        logger.info("Connected to MQTT Broker")
        self.mqtt_cli.subscribe("/oxe/#")  
        self.ready = True

    def add_msg_handler(self, topic, callback):
        self.dispatch_dict[topic] = callback

    def on_message(self,client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic    
        
        if topic in self.dispatch_dict:
            callback = self.dispatch_dict[topic]
            callback(topic,payload)

#=============================================
# HomeView
#=============================================
class HomeView:
    __instance = None
    @staticmethod 
    def instance():
        """ Static access method. """
        if HomeView.__instance == None:
            HomeView()
        return HomeView.__instance

    def __init__(self):
        if HomeView.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            HomeView.__instance = self
        self.conf_dict = {}
        self.conf_list_topic = '/oxe/home/conf/list'
        self.curr_conf = None
        self.curr_source = None
        self.curr_sink1 = None
        self.curr_sink2 = None
        self.pa_module_list = []


    def init(self):
        self.load_conf()

    def load_conf(self):
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

        mqtt_cli.pub('/oxe/home/vol_ctrl1/device_name', sink1)
        mqtt_cli.pub('/oxe/home/vol_ctrl2/device_name', sink2)        
        self.build_audio_conf()
    
    def build_audio_conf(self):                
        try:
            self.destroy_audio_conf() #destroy previous audio conf
            
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
            
            mqtt_cli.pub('/oxe/home/status', 'ready')
        except:
            mqtt_cli.pub('/oxe/home/notification', 'Error on creating pa modules')
            mqtt_cli.pub('/oxe/home/status', 'Error: audio port not ready')
            self.destroy_audio_conf()
            self._log_exception()


    def destroy_audio_conf(self):
        try:            
            for i in self.pa_module_list:
                pa.module_unload(i)
            self.pa_module_list.clear()
            self.curr_source = None
            self.curr_sink1 = None
            self.curr_sink2 = None            
        except:
            mqtt_cli.pub('/oxe/home/notification', 'Error on removing pa module')
            mqtt_cli.pub('/oxe/home/status', 'Error: cleaning pa modules')
            self._log_exception()


    def on_msg_vol_ctrl1_vol(self,topic,payload):
        logger.info('on_msg_vol_ctrl1_vol %s', payload)
        try:
            vol = int(payload)
            if self.curr_sink1 != None:
                pa.volume_set_all_chans(self.curr_sink1, vol / 100 )
        except:
            self._log_exception()


    def on_msg_vol_ctrl2_vol(self,topic,payload):
        logger.info('on_msg_vol_ctrl2_vol %s', payload)
        try:
            vol = int(payload)
            if self.curr_sink2 != None:
                pa.volume_set_all_chans(self.curr_sink2, vol / 100 )
        except:
            self._log_exception()

    def _log_exception(self):
        ex = str(sys.exc_info()[1])
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)
        func_name = stk[0][2]            
        logger.error("Error : " + func_name + ' : ' + ex)



#=============================================
# Audio Controls
#=============================================

class AudioCtlView:
    __instance = None
    @staticmethod 
    def instance():
        """ Static access method. """
        if AudioCtlView.__instance == None:
            AudioCtlView()
        return AudioCtlView.__instance

    def __init__(self):
        if AudioCtlView.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            AudioCtlView.__instance = self
        
        self.audio_port = ''
                

#=============================================
# BT Speaker
#=============================================

class BtSpeakerView:
    __instance = None
    @staticmethod 
    def instance():
        """ Static access method. """
        if BtSpeakerView.__instance == None:
            BtSpeakerView()
        return BtSpeakerView.__instance

    def __init__(self):
        if BtSpeakerView.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            BtSpeakerView.__instance = self
        
        self.bt_spkr_dev = None #Device object
        self.status_topic = '/oxe/bt_spkr/status'
        self.bt_spkr_list = '/oxe/bt_spkr/list'       
        self.default_hci  = 'hci1'         

    def init(self):
        self.load_conf()
        mqtt_cli.pub(self.status_topic, '-')
    
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


    def send_msg_select_spkr(self):
        mqtt_cli.pub(self.status_topic, payload='select a speaker')
    

    def on_connect(self,dev):
        if dev == None:
            self.send_msg_select_spkr()
            return
        logger.info('Device connected : [ %s : %s ]' , dev.alias , dev.address )
        self.send_msg_connect_state()

    def on_disconnect(self,dev):
        if dev == None:
            self.send_msg_connect_state()
            return    
        logger.info('Device disconnected : [ %s : %s ]' , dev.alias , dev.address )
        self.send_msg_connect_state()

    def send_msg_connect_state(self):
        if self.bt_spkr_dev == None:
            mqtt_cli.pub(self.status_topic, payload='not connected')
            return        
        if self.bt_spkr_dev.connected:
            mqtt_cli.pub(self.status_topic, payload='connected')            
        else:
            mqtt_cli.pub(self.status_topic, payload='not connected')


    def on_msg_select(self,topic, payload):
        self.bt_spkr_dev = bt_service.get_device_by_name(payload,self.default_hci)
        if self.bt_spkr_dev == None:
            mqtt_cli.pub(self.status_topic, payload='Not available')
            mqtt_cli.pub('/oxe/bt_spkr/notification','Speaker not available or not paired')
            return
        self.send_msg_connect_state()
    
    def on_msg_connect(self,topic, payload):
        try:
            if self.bt_spkr_dev == None:
                self.send_msg_select_spkr()
                return
            if self.bt_spkr_dev.connected:
                self.send_msg_connect_state()
                logger.info('[%s %s] already connected', self.bt_spkr_dev.address, self.bt_spkr_dev.alias)
                return

            mqtt_cli.pub(self.status_topic, payload='connecting...')
            logger.info('connecting [%s %s]', self.bt_spkr_dev.address, self.bt_spkr_dev.alias)
            self.bt_spkr_dev.connect()
        except:
            self.send_msg_connect_state()
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
            self.send_msg_connect_state()
            self._log_exception()

    def _log_exception(self):
        ex = str(sys.exc_info()[1])
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)
        func_name = stk[0][2]            
        logger.error("Error : " + func_name + ' : ' + ex)



#=============================================
# OXE SPOT 
#=============================================


class OxeSpot:
    __instance = None
    @staticmethod 
    def instance():
        """ Static access method. """
        if OxeSpot.__instance == None:
            OxeSpot()
        return OxeSpot.__instance

    def __init__(self):
        if OxeSpot.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            OxeSpot.__instance = self

    def init(self):        
        #=============================================
        # Audio
        #=============================================
        self.print_audio_sources()
        self.print_audio_sinks()
        
        #set default capture source of card 1 (USB) to Mic
        os.system('amixer -c 1 cset \'numid=16\' 0')
        #amixer -c 1 cget 'numid=16' :
        # type=ENUMERATED,access=rw------,values=1,items=4
        # Item #0 'Mic'
        # Item #1 'Line'
        # Item #2 'IEC958 In'
        # Item #3 'Mixer'
        # values=0
        

        #=============================================
        # Callbacks
        #=============================================
        mqtt_cli.add_msg_handler('/oxe/app',self.on_msg)
        
        mqtt_cli.add_msg_handler('/oxe/home/conf/select', home_vw.on_msg_conf_select)    
        mqtt_cli.add_msg_handler('/oxe/home/vol_ctrl1/vol', home_vw.on_msg_vol_ctrl1_vol)    
        mqtt_cli.add_msg_handler('/oxe/home/vol_ctrl2/vol', home_vw.on_msg_vol_ctrl2_vol)

        mqtt_cli.add_msg_handler('/oxe/bt_spkr_vw/select', bt_spkr_vw.on_msg_select)
        mqtt_cli.add_msg_handler('/oxe/bt_spkr_vw/connect',bt_spkr_vw.on_msg_connect)
        mqtt_cli.add_msg_handler('/oxe/bt_spkr_vw/disconnect',bt_spkr_vw.on_msg_disconnect)


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
        if hci0 != None:
            hci0.on_connect = bt_spkr_vw.on_connect
            hci0.on_disconnect = bt_spkr_vw.on_disconnect
        if hci1 != None:
            hci1.on_connect = bt_spkr_vw.on_connect
            hci1.on_disconnect = bt_spkr_vw.on_disconnect

        #=============================================
        logger.info('ready')
        mqtt_cli.pub('/oxe/home/status', payload='ready')


    def on_msg(self,topic, payload):
        if payload == 'stop':
            self.stop()
    
    def print_audio_sources(self):
        for so in pa.sink_list():
            logger.info("Audio source: %s" ,so)

    def print_audio_sinks(self):
        for si in pa.sink_list():            
            logger.info("Audio sink: %s" , si)

    def stop(self):
        stop()


#=============================================
# Global initalization
#=============================================

loop = GLib.MainLoop()

def stop():
    logger.info('done')
    mqtt_cli.pub('/oxe/status', payload='Off')
    home_vw.destroy_audio_conf()
    bt_service.stop()        
    loop.quit()
    sys.exit(0)

def signal_handler(sig, frame):
    stop()
    
signal.signal(signal.SIGINT, signal_handler)

mqtt_cli = MqttClient.instance()
mqtt_cli.init()
bt_service = BtService.instance()

pa = pulsectl.Pulse('oxe_spot')
pa.connect(autospawn=True, wait=True)

audio_ctl_vw = AudioCtlView.instance()
bt_spkr_vw = BtSpeakerView.instance()
home_vw = HomeView.instance()

home_vw.init()
bt_spkr_vw.init()


#=============================================
# Main
#=============================================

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    oxe_spot = OxeSpot.instance()
    oxe_spot.init()    
    loop.run()