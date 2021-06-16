import dbus
import time
import logging
import sys
import subprocess
import pulsectl

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
        self.pulse = pulsectl.Pulse('oxe_spot')
        self.pulse.connect(autospawn=True, wait=True)

    def start(self):
        pass

    def stop(self):
        pass

    def get_sink_by_descr(self, descr):
        for si in self.pulse.sink_list():
            if si.description == descr:
                return si
        return None

    def print_sources(self):
        for so in self.pulse.sink_list():
            logger.info("Audio source: %s" ,so)

    def print_sinks(self):
        for si in self.pulse.sink_list():            
            logger.info("Audio sink: %s" , si)
            
    
    def combine_sinks(self, sink1,sink2):
        pass


    def _source_volume_monitor(self):
        logger.info('Source volume monitor')
        def volume_changed_handler(interface, changed, invalidated, path):
            if 'Volume' in changed:
                self.source_vol = int(changed['Volume'])
                pa_vol=self.source_vol*1000                
                logger.info('Vol changed=%d , pa_volume=%d', self.source_vol, pa_vol )
            
            
        self.bus.add_signal_receiver(volume_changed_handler,
                                     bus_name='org.bluez',
                                     dbus_interface=dbus.PROPERTIES_IFACE,
                                     signal_name='PropertiesChanged',
                                     path_keyword='path')

