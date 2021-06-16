import dbus
import time
import logging
import os, sys, traceback
import subprocess


from bluezero           import adapter
from bluezero           import device
from bluezero           import tools

from bluetooth.bt_agent import BtAgentService

logger = logging.getLogger(name='bt_service')


class BtService:
    __instance = None
    @staticmethod 
    def instance():
        """ Static access method. """
        if BtService.__instance == None:
            BtService()
        return BtService.__instance

    def __init__(self):
        if BtService.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            BtService.__instance = self
            
        agent = BtAgentService()
        agent.start()

    
    def start(self):
        pass
    
    def stop(self):
        pass    

    def get_device_by_addr(self,dev_addr,hci_name):
        try:
            adapter = self.adapter_get_instance(hci_name)
            if adapter == None:
                return None

            for d in list(device.Device.available()):
                if dev_addr == d.address and d.adapter == adapter.address:
                    return d
            return None
        except:
            self._log_exception()
            return None

    def get_device_by_name(self,dev_name,hci_name):
        try:
            adapter = self.adapter_get_instance(hci_name)
            if adapter == None:
                return None

            for d in list(device.Device.available()):
                if dev_name == d.alias and d.adapter == adapter.address:
                    return d
            return None
        except:
            self._log_exception()
            return None


    def discover_and_connect(self, dev_addr , hci_name, attempts=8):
        try:
            target_dev=None
            adapter = self.adapter_get_instance(hci_name)
            if adapter == None:
                logger.error('Invalid adapter [ %s ]' , hci_name )
                return

            def _scan_target_device():
                logger.info('Scanning [ %s ] ...' , dev_addr)
                def _on_device_found(self,dev):        
                    if dev.address == dev_addr:
                        nonlocal target_dev
                        target_dev = dev
                    
                adapter._on_device_found = _on_device_found
                adapter.nearby_discovery(timeout=10)

            def _pair_target_device():
                if target_dev.paired:
                    return
                logger.info('Pairing [ %s ] ...' , dev_addr)
                target_dev.pair()

            cnt=0
            while cnt < attempts:
                cnt +=1 

                target_dev = self.get_device_by_addr(dev_addr,hci_name)                                
                logger.info('Trying to connect [ %s ] , attempt %d of %d' , dev_addr , cnt ,  attempts)
                        
                if target_dev == None:
                    _scan_target_device()
                else: #found target_dev                    
                    _pair_target_device()
                    target_dev.trusted = True
                    target_dev.connect()
                    if target_dev.paired and target_dev.connected:
                        logger.info('connected!')
                        return

            if cnt == attempts:
                logger.info('Cant find target device [ %s ]' , dev_addr )                
        except:
            self._log_exception()            


    def adapter_set_class(self, hci_index, major, minor):
        try: 
            cmd="sudo btmgmt --index " + str(hci_index) + " class " + major +  " " + minor
            subprocess.run([cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        except:
            self._log_exception()            


    def adapter_get_instance(self,hci_name):
        try:        
            for ad in list(adapter.Adapter.available()):
                if hci_name in ad.path:
                    return ad
            return None
        except:
            self._log_exception()
            return None

    def adapter_set_discoverable(self,hci_name, timeout=180):
        try:        
            for ad in list(adapter.Adapter.available()):
                if hci_name in ad.path:
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
                    break
        except:
            self._log_exception()

    def adapter_get_devices_list(self, hci_name):
        dev_list = []
        try:
            adapter = self.adapter_get_instance(hci_name)
            if adapter == None:
                return dev_list

            for d in list(device.Device.available()):
                if (d.adapter == adapter.address):
                    dev_list.append(d)
            return dev_list
        except:
            self._log_exception()
            return dev_list

    def adapter_get_paired_devices_list(self, hci_name):        
        try:
            dev_list = []
            for d in self.adapter_get_devices_list(hci_name):
                if d.paired == True:
                    dev_list.append(d)
            return dev_list
        except:
            self._log_exception()


    def device_connect(self, dev_addr):
        try:
            for d in list(device.Device.available()):
                if d.address == dev_addr:
                    if not d.connected:
                        logger.info('Connecting [ %s ]' , d.alias )
                        d.disconnect()
        except:
            self._log_exception()

    def device_disconnect(self, dev_addr):
        try:
            for d in list(device.Device.available()):
                if d.address == dev_addr:
                    if d.connected:
                        logger.info('Disconnecting [ %s ]' , d.alias )
                        d.disconnect()
        except:
            self._log_exception()
    
    def _log_exception(self):
        ex = str(sys.exc_info()[1])
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)
        func_name = stk[0][2]            
        logger.error("Error : " + func_name + ' : ' + ex)


    
           





