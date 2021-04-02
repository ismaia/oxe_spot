import logging
import sys
import dbus
import signal
import time
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



if __name__ == '__main__':
    logger.info('Ready')
    DBusGMainLoop(set_as_default=True)

    hci0='hci0'
    hci1='hci1'
    
    hci0_name='oxe_spot'
    hci1_name='a2dp_port1'    

    bt_speaker1='SoundCore 2'
    bt_speaker2='MEGABOOM 3'
    

    # bt_service.adapter_on(hci0)
    # bt_service.adapter_on(hci1)
    # bt_service.adapter_set_alias(hci0, hci0_name)    
    # bt_service.adapter_set_alias(hci1, hci1_name)
    
    
    # bt_service.adapter_set_discoverable(hci0)        
    # #bt_service.discover_and_connect(bt_speaker1, hci0)
    # bt_service.discover_and_connect(bt_speaker2, hci1)

    
    loop = GLib.MainLoop()
    loop.run()