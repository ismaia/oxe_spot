import logging
import sys
import dbus
import signal
import time
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from bluetooth.oxe_bt_service import OxeBtService


logging.basicConfig(level=logging.DEBUG, format='%(name)s :: %(message)s')
logger = logging.getLogger(name='oxe_spot')

def signal_handler(sig, frame):
    logger.info('done')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def dev_added_callback(dev):
    print(dev.address , " " , dev.alias)


def bt_speaker_connect_test():
    logger.info('')
    logger.info('Devices on adapter [' + bt_adapter_main + '] ')
    for d in bt_service.get_devices(bt_adapter_main):
        logger.info(d.alias + ' : ' + d.address)
    logger.info('')
    logger.info('Paired devices on adapter [' + bt_adapter_main + '] ')
    for d in bt_service.get_paired_devices(bt_adapter_main):
        logger.info(d.alias + ' : ' + d.address)

    bt_service.disconnect_device(bt_speaker1)
    bt_service.disconnect_device(bt_speaker2)

    bt_service.connect_device(bt_speaker1, bt_adapter_a2dp_port1)
    bt_service.disconnect_device(bt_speaker1)
    bt_service.connect_device(bt_speaker2, bt_adapter_a2dp_port1)


if __name__ == '__main__':
    logger.info('Ready')
    DBusGMainLoop(set_as_default=True)

    bt_adapter_main='oxe_spot'
    bt_adapter_a2dp_port1='a2dp_port1'
    bt_speaker1='SoundCore 2'
    bt_speaker2='MEGABOOM 3'

    bt_service = OxeBtService()

    bt_service.set_adapter_alias('hci0', bt_adapter_main)
    bt_service.set_adapter_alias('hci1', bt_adapter_a2dp_port1)    
    bt_service.set_adapter_pairable(bt_adapter_a2dp_port1)

    
    loop = GLib.MainLoop()
    loop.run()