import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from bluetooth import BluetoothService


if __name__ == '__main__':
    print('OXE Spot')
    DBusGMainLoop(set_as_default=True)

    bt_service = BluetoothService()

    bt_service.adapter.bind_name('hci0', 'oxe_spot')
    bt_service.adapter.bind_name('hci1', 'a2dp_sink')

    bt_speaker1='SoundCore2'
    bt_service.device.register(bt_speaker1)

    if bt_service.device.is_connected(bt_speaker1):
        pass


    loop = GLib.MainLoop()
    loop.run()    

    