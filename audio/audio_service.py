import dbus
import time
import logging
import sys
import subprocess


logger = logging.getLogger(name='audio_service')
    
class AudioService:
    __instance = None

    @staticmethod 
    def instance():
        """ Static access method. """
        if AudioService.__instance == None:
            AudioService()
        return AudioService.__instance

    def __init__(self):
        if AudioService.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            AudioService.__instance = self

        self.bus = dbus.SystemBus()
        self.source_vol = 0
        self._source_volume_monitor()

    def start(self):
        pass
    
    def stop(self):
        pass



    def get_default_sink(self):
        cmd="pactl info | grep -i \'default sink\'"
        process = subprocess.run([cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        cmd_out=process.stdout
        out_list=cmd_out.split(':')
        if out_list:
            default_sink=out_list[1]
            return default_sink.strip()
        return None


    def get_default_source(self):
        cmd="pactl info | grep -i \'default source\'"
        process = subprocess.run([cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        cmd_out=process.stdout
        out_list=cmd_out.split(':')
        if out_list:
            default_source=out_list[1]
            return default_source.strip()
        return None
    
    def set_default_source_volume(self,vol):
        source=self.get_default_source()
        cmd="pactl set-source-volume " + source + " " + str(vol)
        subprocess.run([cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)

    
    def combine_sinks(self, sink1,sink2):
        pass


    def _source_volume_monitor(self):
        logger.info('Source volume monitor')
        def volume_changed_handler(interface, changed, invalidated, path):
            if 'Volume' in changed:
                self.source_vol = int(changed['Volume'])
                pa_vol=self.source_vol*1000
                self.set_default_source_volume(pa_vol)
                logger.info('Vol changed=%d , pa_volume=%d', self.source_vol, pa_vol )
            
            
        self.bus.add_signal_receiver(volume_changed_handler, 
                                     bus_name='org.bluez',
                                     dbus_interface=dbus.PROPERTIES_IFACE,
                                     signal_name='PropertiesChanged',
                                     path_keyword='path')

