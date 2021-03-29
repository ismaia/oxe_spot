import sys
import dbus
import signal
import time
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from bluetooth.bt_service import BtService


def signal_handler(sig, frame):
    print('done')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def test_adapter_rename():
    bt_adapter_main='ad_main1'
    bt_adapter_a2dp_port1='a2dp_port1'

    print('available adapters:')
    bt_service.list_available_adapters()    
    print('renaming adapters...')
    bt_service.set_adapter_alias('hci0', bt_adapter_main)
    bt_service.set_adapter_alias('hci1', bt_adapter_a2dp_port1)    
    print('adapters after rename:')
    bt_service.list_available_adapters()    
    print('devices list:')
    bt_service.list_available_devices()    
    print('--')
    print('--')

    bt_adapter_main='ad_main2'
    bt_adapter_a2dp_port1='a2dp_port2'

    print('available adapters:')
    bt_service.list_available_adapters()    
    print('renaming adapters...')
    bt_service.set_adapter_alias('hci0', bt_adapter_main)
    bt_service.set_adapter_alias('hci1', bt_adapter_a2dp_port1)    
    print('adapters after rename:')
    bt_service.list_available_adapters()    
    print('devices list:')
    bt_service.list_available_devices()    
    print('--')

def dev_added_callback(dev):
    print(dev.address , " " , dev.alias)


if __name__ == '__main__':
    
    print('OXE Spot\n')
    # DBusGMainLoop(set_as_default=True)

    bt_adapter_main='oxe_spot'
    bt_adapter_a2dp_port1='a2dp_port1'

    bt_service = BtService()

    bt_service.set_adapter_alias('hci0', bt_adapter_main)
    bt_service.set_adapter_alias('hci1', bt_adapter_a2dp_port1)    
    print('adapters:')
    bt_service.list_available_adapters()    
    print('devices list:')
    bt_service.list_available_devices()    
    print('--')
    bt_service.connect_device('SoundCore 2', bt_adapter_a2dp_port1)

    loop = GLib.MainLoop()
    loop.run()    