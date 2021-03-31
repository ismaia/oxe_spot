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

def signal_handler(sig, frame):
    logger.info('done')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


# def bt_speaker_connect_test():
#     logger.info('')
#     logger.info('Devices on adapter [' + bt_adapter_main + '] ')
#     for d in bt_service.adapter_get_devices_list(bt_adapter_main):
#         logger.info(d.alias + ' : ' + d.address)
#     logger.info('')
#     logger.info('Paired devices on adapter [' + bt_adapter_main + '] ')
#     for d in bt_service.adapter_get_paired_devices_list(bt_adapter_main):
#         logger.info(d.alias + ' : ' + d.address)

#     bt_service.device_disconnect(bt_speaker1)
#     bt_service.device_disconnect(bt_speaker2)

#     bt_service.device_connect(bt_speaker1, bt_adapter_a2dp_port1)
#     bt_service.device_disconnect(bt_speaker1)
#     bt_service.device_connect(bt_speaker2, bt_adapter_a2dp_port1)



if __name__ == '__main__':
    logger.info('Ready')
    DBusGMainLoop(set_as_default=True)

    bt_adapter_main='oxe_spot'
    bt_adapter_a2dp_port1='oxe_spot1'
    bt_speaker1='SoundCore 2'
    bt_speaker2='MEGABOOM 3'

    bt_service = BtService()

    bt_adpter_test='oxe_spot_test'
    bt_service.adapter_on('hci0')
    bt_service.adapter_on('hci1')
    bt_service.adapter_set_alias('hci0', bt_adapter_main)
    bt_service.adapter_off('hci0')
    bt_service.adapter_set_alias('hci1', bt_adpter_test)
    bt_service.adapter_discoverable(bt_adpter_test)

    audio_service = AudioService()
    audio_service.start_source_volume_monitor()
    
    
    loop = GLib.MainLoop()
    loop.run()