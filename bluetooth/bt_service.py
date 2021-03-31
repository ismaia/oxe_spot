import dbus
import time
import logging
import os, sys, traceback

from bluezero           import adapter
from bluezero           import device
from bluezero           import tools

from bluetooth.bt_agent import BtAgentService

logger = logging.getLogger(name='bt_service')


class BtService:

    def __init__(self):

        agent = BtAgentService()
        agent.start()        

    def adapter_get_instance(self,adapter_alias):
        try:        
            for ad in list(adapter.Adapter.available()):
                if adapter_alias == ad.alias:
                    return ad
            return None
        except:
            self._log_exception()
            return None

    def adapter_discoverable(self,adapter_alias, timeout=120):
        try:        
            for ad in list(adapter.Adapter.available()):
                if adapter_alias == ad.alias:
                    ad.pairable=True                    
                    ad.discoverable=True
        except:            
            self._log_exception()

    def adapter_on(self, hci_name):
        try:
            for ad in list(adapter.Adapter.available()):
                if hci_name in ad.path:                
                    ad.powered = True
                    time.sleep(0.2) #wait dbus transaction
                    break
        except:          
            self._log_exception()

    def adapter_off(self, hci_name):
        try:
            for ad in list(adapter.Adapter.available()):
                if hci_name in ad.path:                
                    ad.powered = False                    
                    time.sleep(0.2) #wait dbus transaction
                    break
        except:
            self._log_exception()


    def adapter_set_alias(self, hci_name, alias):
        try:
            for ad in list(adapter.Adapter.available()):
                if hci_name in ad.path:
                    ad.alias = alias #set its new name
                    time.sleep(0.2) #wait dbus transaction
                    break
        except:
            self._log_exception()

    def adapter_get_devices_list(self, adapter_alias):
        dev_list = []
        try:
            adapter = self.adapter_get_instance(adapter_alias)            
            if adapter == None:
                return dev_list
            
            for d in list(device.Device.available()):            
                if (d.adapter == adapter.address):
                    dev_list.append(d)
            return dev_list
        except:
            self._log_exception()
            return dev_list

    def adapter_get_paired_devices_list(self, adapter_alias):        
        try:
            dev_list = []
            for d in self.adapter_get_devices_list(adapter_alias):
                if d.paired == True:
                    dev_list.append(d)
            return dev_list
        except:
            self._log_exception()



    def device_get_instance(self,device_alias,adapter_alias):
        try:        
            adapter = self.adapter_get_instance(adapter_alias)
            if adapter == None:
                return None

            for d in list(device.Device.available()):
                if device_alias == d.alias and d.adapter == adapter.address:
                    return d
            return None
        except:
            self._log_exception()
            return None


    def device_disconnect(self, dev_alias):        
        try:
            for d in list(device.Device.available()):
                if d.alias == dev_alias:
                    if d.connected:
                        logger.info('Disconnecting [ ' + dev_alias + ' ]' )
                        d.disconnect()
        except:
            self._log_exception()



    def device_connect(self, dev_alias, adapter_alias, attempts=8):    
        try:
            target_dev=None
            adapter = self.adapter_get_instance(adapter_alias)
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

                target_dev = self.device_get_instance(dev_alias,adapter_alias)            
                logger.info('Trying to connect [ ' + dev_alias + ' ], attempt ' + str(cnt) +' of ' + str(attempts))
                        
                if target_dev == None:
                    _scan_target_device()
                else: #found target_dev
                    logger.info('Device ' + target_dev.alias + ' found on adapter [ ' + adapter.alias + ' ]' )
                    _pair_target_device()
                    target_dev.trusted = True
                    target_dev.connect()
                    if target_dev.paired and target_dev.connected:
                        logger.info('Device [ ' + target_dev.alias + ' ] connected !')
                        return

            if cnt == attempts:
                logger.info('Cant find target device [ ' + dev_alias + ' ]' )
                
        except:
            self._log_exception()            



    def _log_exception(self):
        ex = str(sys.exc_info()[1])
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)
        func_name = stk[0][2]            
        logger.error("Error : " + func_name + ' : ' + ex)


    
           





