import logging

from bluezero import adapter
from bluezero import device
from bluezero import tools


def dev_added_callback(dev):
    print(dev.address , " " , dev.alias)

def main():
    adapter_list = adapter.list_adapters() 
    for a in adapter_list:
       adpt = adapter.Adapter(a)
       print('address: ', adpt.address)
       print('name: ', adpt.name)
       print('alias: ', adpt.alias)
       print('powered: ', adpt.powered)
       print('pairable: ', adpt.pairable)
       print('pairable timeout: ', adpt.pairabletimeout)
       print('discoverable: ', adpt.discoverable)
       print('discoverable timeout: ', adpt.discoverabletimeout)
       print('discovering: ', adpt.discovering)
       print('Powered: ', adpt.powered)
       if not adpt.powered:
           adpt.powered = True
           print('Now powered: ', adpt.powered)

    print('Start discovering')    
    adapter0 = adapter.Adapter(adapter_list[0])
    adapter0.on_device_found = dev_added_callback
    adapter0.nearby_discovery(timeout=15)
    adapter0.alias = 'Inspi'


    print('Nearby Devices:')
    devs = device.Device.available()
    for d in devs:
        print(d.address , ' ' , d.alias)
        # if d.alias == 'YET-M1':
        #   yet_m1_device = d
        # if d.alias == 'MEGABOOM 3':
        #   megaboom3_device = d

        
    # for i in range(4):
    #    if yet_m1_device.paired:
    #        print('yet_m1 paired')
    #        yet_m1_device.trusted = True
    #        break
    #    else:
    #        print('trying to pair yet_m1, attempt ' , i) 
    #        yet_m1_device.pair()

    # for i in range(4):
    #    if megaboom3_device.paired:
    #        print('megaboom3 paired')
    #        megaboom3_device.trusted = True
    #        megaboom3_device.connect()
    #        break
    #    else:
    #        print('trying to pair megaboom3, attempt ' , i) 
    #        megaboom3_device.pair()



if __name__ == '__main__':
    print(__name__)
    # logger = tools.create_module_logger('adapter')
    # logger.setLevel(logging.DEBUG)
    main()
