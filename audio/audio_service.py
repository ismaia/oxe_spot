import dbus
import time
import logging
import sys
import threading

logger = logging.getLogger(name='audio_service')
    
class AudioService:
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.source_vol = 0

    def start(self):
        pass
    
    def stop(self):
        pass


    def start_source_volume_monitor(self):
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

