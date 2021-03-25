import dbus
from gi.repository import GLib

from bluezero import adapter
from bluezero import device
from bluezero import tools

class BtService:

    def __init__(self):
        self.adapter_list = []        
        self.adapter_dict = {}
        for a in adapter.list_adapters(): 
            ad = adapter.Adapter(a)
            self.adapter_list.append(ad)
        self.device_list = list(device.Device.available())

    
    def availabe_devices(self):
        return self.device_list

    def set_adapter_name(self, hci_name, name):
        for ad in self.adapter_list:
            if hci_name in ad.path:
                ad.alias = name
                self.adapter_dict[ad.alias] = ad

    def list_available_devices(self):
        for d in self.device_list:
            print('[', d.address, ' - ', d.name ,']')
    
    def connect_device(self, dev_name, adapter_name):
        for d in self.device_list:
            if d.alias == dev_name:
                print('Connecting device [', dev_name ,' - ', d.address , '] ...')
                if not d.paired:
                    pass


