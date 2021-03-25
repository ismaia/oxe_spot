import dbus
from gi.repository import GLib

from bluezero import adapter
from bluezero import device
from bluezero import tools



class BluetoothService:
    """Bluetooth Service Class
    """

    def __init__(self):
        self.device_list = []
        self.adapter_list = []
        for a in adapter.list_adapters(): 
            ad = adapter.Adapter(a)
            self.adapter_list.append(ad)
            for d in device.Device.available(ad.address):
                self.device_list.append(d)
    

    def set_adapter_name(self,index, name):
        if index < len(self.adapter_list):
            self.adapter_list[index].alias = name            

    def register_device(self, name):
        pass

    def connect_device(self,name):
        pass
    
    def disconnect_device(self,name):
        pass

    def list_devices(self):
        for d in self.device_list:
            d_adapter = adapter.Adapter(d.adapter)
            print(d.name , d.address , '[' , d_adapter.alias , ']' )


        
   
    

