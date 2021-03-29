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
        self.discovered_devices_dict = {}
            
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
        
        target_dev = None
        retry = 0
        while retry < 3:
            self._refresh_devices()
            adapter = self._get_adapter(adapter_alias)
            if adapter == None:
                print('Error: Adapter not found: ', adapter_alias)            
                return        

            #check if device is already available on this adapter
            if self.device_alias_dict[dev_alias].adapter == adapter.address:
                print('Device', dev_alias , 'is available on ' , adapter.alias)
                target_dev = self.device_alias_dict[dev_alias]
                if target_dev.paired:
                    print('Trying to connect device :', dev_alias , '=>' ,  adapter.alias , '(' , adapter.address , ')' )
                    target_dev.connect()
                self._pair_device(target_dev)
                                
            if dev_alias in self.discovered_devices_dict:
                target_dev = self.discovered_devices_dict[dev_alias]
            else:
                self._scan_device(dev_alias, adapter_alias)

            self._refresh_devices()
            retry = retry + 1



    def _scan_device(self, dev_alias, adapter_alias):        
        retry = 0
        self.discovered_devices_dict.clear()
        while retry < 5:
            if self._get_adapter(adapter_alias) == None:        
                print('Adapter not found:',  adapter_alias)
                break
            print('Device scanning: ' , dev_alias , ', attempt ', retry ,' ...')
            ad = self.adapter_alias_dict[adapter_alias]
            ad.on_device_found = self._on_device_found
            ad.nearby_discovery(timeout=10)
            if dev_alias in self.discovered_devices_dict:
                dev = self.discovered_devices_dict[dev_alias]
                print('Device Found :', dev.alias, ' (' , dev.address , ')' )                
                break
            else:
                print('Device not found:', dev_alias)
            retry = retry + 1

        self._refresh_devices()
        return

    
    def _pair_device(self,dev):
        retry = 0
        while not dev.paired and retry < 3:
            print('Trying to pair device :' , dev.alias)
            dev.pair()            
            retry = retry + 1

    def _refresh_devices(self):
        self.device_alias_dict.clear()
        self.device_addr_dict.clear()
        for d in list(device.Device.available()):
            self.device_alias_dict[d.alias] = d
            self.device_addr_dict[d.address] = d

        
                
    def _on_device_found(self,dev):        
        self.discovered_devices_dict[dev.alias] = dev

    def _on_device_connect(self,dev):
        pass

    def _on_device_disconnect(self,dev):
        pass

    def _get_adapter(self, adapter_alias):
        if adapter_alias in self.adapter_alias_dict:
            return self.adapter_alias_dict[adapter_alias]            
        return None
        


        # for d in self.device_list:
        #     if d.alias == dev_alias:
        #         print('Connecting device [', dev_alias ,' - ', d.address , '] ...')
        #         if not d.paired:
        #             pass

           





