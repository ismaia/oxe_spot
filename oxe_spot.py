import dbus
from dbus.mainloop.glib import DBusGMainLoop
from bluetooth.service import BtService

if __name__ == '__main__':
    
    print('OXE Spot\n')

    bt_adapter_main='oxe_spot'
    bt_adapter_a2dp='a2dp_sink'
    bt_service = BtService()
    bt_service.set_adapter_name('hci0', bt_adapter_main)
    bt_service.set_adapter_name('hci1', bt_adapter_a2dp)

    bt_service.list_available_devices()    
    bt_service.connect_device('SoundCore 2', bt_adapter_a2dp)




    # loop = GLib.MainLoop()
    # loop.run()    

    