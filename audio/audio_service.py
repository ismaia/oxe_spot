import dbus
import time
import logging
import sys
import threading

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
        self.source_volume_monitor()

    def start(self):
        pass
    
    def stop(self):
        pass


    def source_volume_monitor(self):
        logger.info('Source volume monitor')
        def volume_changed_handler(interface, changed, invalidated, path):
            if 'Volume' in changed:
                self.source_vol = int(changed['Volume'])
                logger.info('Vol changed : ' + str(self.source_vol))
                
            
        self.bus.add_signal_receiver(volume_changed_handler, 
                                     bus_name='org.bluez', 
                                     dbus_interface=dbus.PROPERTIES_IFACE,
                                     signal_name='PropertiesChanged',
                                     path_keyword='path')

