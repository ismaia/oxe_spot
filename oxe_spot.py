import dbus
from dbus.mainloop.glib import DBusGMainLoop

from gi.repository import GLib
from bluezero import adapter
from bluezero import device
from bluezero import tools



class BtAdapterMonitor:
    def __init__(self, hci_index, alias):
        pass


class BtSpeakerMonitor:
    def __init__(self, spk_name):
        pass

    def connect(self):
        pass


class AudioMonitor:
    def __init__(self, dev_name):
        pass




if __name__ == '__main__':
    
    print('OXE Spot\n')

    bt_adapter0 = BtAdapterMonitor(hci_index=0, alias='oxe_spot')
    bt_adapter1 = BtAdapterMonitor(hci_index=1, alias='a2dp_sink')
    bt_speaker1 = BtSpeakerMonitor('SoundCore 2')
    bt_speaker1.connect()



    # loop = GLib.MainLoop()
    # loop.run()    

    