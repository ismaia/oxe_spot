import dbus
import time
import logging

from bluezero      import adapter
from bluezero      import device
from bluezero      import tools
from gi.repository import GLib

logging.basicConfig(level=logging.DEBUG, format='%(name)s :: %(message)s')
logger = logging.getLogger(name='bt_service')


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
                

    
    def connect_device(self, dev_alias, adapter_alias, attempts=8):    
        target_dev=None
        adapter = self.get_adapter(adapter_alias)
        if adapter == None:
            logger.error('Invalid adapter [ ' + adapter_alias + ' ]' )
            return

        def _scan_target_device():
            logger.info('Scanning...')
            def _on_device_found(self,dev):        
                if dev.alias == dev_alias:
                    nonlocal target_dev
                    target_dev = dev
                
            adapter._on_device_found = _on_device_found
            adapter.nearby_discovery(timeout=10)

        def _pair_target_device():
            if target_dev.paired:
                return
            logger.info('Pairing...')
            target_dev.pair()


        cnt=0
        while cnt < attempts:
            cnt +=1 

            target_dev = self.get_device(dev_alias,adapter_alias)            
            logger.info('Trying to connect device [ ' + dev_alias + ' ], attempt ' + str(cnt) +' of ' + str(attempts))
                    
            if target_dev == None:
                _scan_target_device()
            else: #found target_dev
                logger.info('Device ' + target_dev.alias + ' found on adapter [ ' + adapter.alias + ' ]' )
                _pair_target_device()
                target_dev.connect()
                if target_dev.paired and target_dev.connected:
                    logger.info('Device [ ' + target_dev.alias + ' ] connected !')
                    return
        
        if cnt == attempts:
            logger.info('Cant find target device [ ' + dev_alias + ' ]' )

            



                
            


        # def _pair_device(self,dev_alias, attempts=4):
        #     pass
            
        #     ad = self.get_adapter(adapter_alias)
        #     if ad == None:
        #         print('Adapter not found:',  adapter_alias)
        #         return
        #     ad.on_device_found = _on_device_found

        #     #d = sef.get_device(dev_alias, adapter_alias);

        # pass
     

        



    

                




    
           





