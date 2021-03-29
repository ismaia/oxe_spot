import dbus
from gi.repository import GLib
import time

from bluezero import adapter
from bluezero import device
from bluezero import tools



class BtService:

    def __init__(self):
        pass


    def get_adapter(self,adapter_alias):
        for ad in list(adapter.Adapter.available()):
            if adapter_alias == ad.alias:
                return ad
        return None
    
    def get_device(self,device_alias,adapter_alias):
        adapter = self.get_adapter(adapter_alias)
        if adapter == None:
            return None

        for d in list(device.Device.available()):
            if device_alias == d.alias and d.adapter == adapter.address:
                return d
        return None

    def get_devices(self, adapter_alias):
        adapter = self.get_adapter(adapter_alias)
        dev_list = []
        if adapter == None:
            return dev_list
        
        for d in list(device.Device.available()):            
            if (d.adapter == adapter.address):
                dev_list.append(d)
        return dev_list
            
    def get_paired_devices(self, adapter_alias):        
        dev_list = []
        for d in self.get_devices(adapter_alias):
            if d.paired == True:
                dev_list.append(d)
        return dev_list

        

    def set_adapter_alias(self, hci_name, alias):
        for ad in list(adapter.Adapter.available()):
            if hci_name in ad.path:                
                ad.alias = alias #set its new name
                time.sleep(0.2) #wait dbus transaction
                break
        
    def list_available_adapters(self):
        for ad in list(adapter.Adapter.available()):
            print( ad.alias ,'(' , ad.address ,')' )

    def list_available_devices(self):
        for d in list(device.Device.available()):
            print( d.alias ,'(' , d.address ,')' )

    
    def connect_device(self, dev_alias, adapter_alias, attempts=5):    
        pass    
        # def _scan_device(self, dev_alias, adapter_alias, attempts=5):
        #     target_dev = None
        #     def _on_device_found(self,dev):        
        #         if dev.alias == dev_alias:
        #             target_dev = dev

        # def _pair_device(self,dev_alias, attempts=4):
        #     pass
            
        #     ad = self.get_adapter(adapter_alias)
        #     if ad == None:
        #         print('Adapter not found:',  adapter_alias)
        #         return
        #     ad.on_device_found = _on_device_found

        #     #d = sef.get_device(dev_alias, adapter_alias);

        # pass
     

        



    

                




    
           





