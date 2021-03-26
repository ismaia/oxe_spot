import dbus
from gi.repository import GLib
import time

from bluezero import adapter
from bluezero import device
from bluezero import tools



class BtService:

    def __init__(self):               
        self.adapter_alias_dict = {}
        self.adapter_addr_dict = {}
        for a in adapter.list_adapters(): 
            ad = adapter.Adapter(a)
            self.adapter_alias_dict[ad.alias] = ad
            self.adapter_addr_dict[ad.address] = ad
            
        self.device_alias_dict = {}
        self.device_addr_dict = {}
        for d in list(device.Device.available()):
            self.device_alias_dict[d.alias] = d
            self.device_addr_dict[d.address] = d


    def get_adapter(self,hci_name):
        for ad in self.adapter_addr_dict.values():
            if hci_name in ad.path:
                return ad
        

    

    def set_adapter_alias(self, hci_name, alias):
        for ad in self.adapter_addr_dict.values():
            if hci_name in ad.path:                    
                old_ad_alias = ad.alias
                if old_ad_alias in self.adapter_alias_dict:
                    del self.adapter_alias_dict[old_ad_alias]
                    self.adapter_alias_dict[alias] = ad
                ad.alias = alias #set its new name
                time.sleep(1) #wait dbus transaction
                break
        

    def list_available_adapters(self):
        for a in self.adapter_addr_dict.values():            
            print( a.alias ,'(' , a.address ,')' )

    def list_available_devices(self):
        for d in self.device_addr_dict.values():
            if d.adapter in self.adapter_addr_dict:
               ad_alias = self.adapter_addr_dict[d.adapter].alias
               print( d.alias ,'(' , d.address ,') => ' , ad_alias, '(' , d.address , ')'  )
            else:
               print( d.alias ,'(' , d.address ,') => (' , d.address , ')' )
    
    def connect_device(self, dev_alias, adapter_alias):
        adapter = None
        if adapter_alias in self.adapter_alias_dict:
            adapter = self.adapter_alias_dict[adapter_alias]
            print('Connecting device :', dev_alias , '=>' ,  adapter.alias , '(' , adapter.address , ')' )
        else:
            print('Error: Adapter not found: ', adapter_alias)
            return
        print(self.device_alias_dict[dev_alias].adapter , adapter.address )

        
        if self.device_alias_dict[dev_alias].adapter == adapter.address:
          print('Device', dev_alias , 'is available on ' , adapter.alias)
        else:
          print('Device', dev_alias , 'is not available on ' , adapter.alias)
          self._discovery(dev_alias, adapter_alias)
          

    def _discovery(self, dev_alias, adapter_alias):
        if adapter_alias not in self.adapter_alias_dict:
            print('Adapter not found:',  adapter_alias)
            return
        print('Discover :' ,dev_alias)
        ad = self.adapter_alias_dict[adapter_alias]
        ad.on_device_found = self._on_device_found
        ad.nearby_discovery()
        
                
    def _on_device_found(self,dev):
        print('on_device_found : ', dev.alias, dev.address)

    def _on_device_connect(self,dev):
        pass

    def _on_device_disconnect(self,dev):
        pass


        # for d in self.device_list:
        #     if d.alias == dev_alias:
        #         print('Connecting device [', dev_alias ,' - ', d.address , '] ...')
        #         if not d.paired:
        #             pass

           





