import dbus
from gi.repository import GLib

from bluezero import adapter
from bluezero import device
from bluezero import tools


# General D-Bus Object Paths
#: The DBus Object Manager interface
DBUS_OBJM_IFACE = 'org.freedesktop.DBus.ObjectManager'
#: DBus Properties interface
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

# General Bluez D-Bus Object Paths
#: BlueZ DBus Service Name
BLUEZ_SERVICE_NAME = 'org.bluez'
#: BlueZ DBus adapter interface
ADAPTER_INTERFACE = 'org.bluez.Adapter1'
#: BlueZ DBus device Interface
DEVICE_INTERFACE = 'org.bluez.Device1'
# Bluez Media D-Bus object paths
#: BlueZ DBus Media player Interface
MEDIA_PLAYER_IFACE = 'org.bluez.MediaPlayer1'



class BluetoothService:
    """Bluetooth Service Class
    """

    def __init__(self):
        """

        """
        self.bus = dbus.SystemBus()

        self.bus.add_signal_receiver( self._interfaces_added_handler,
                                      dbus_interface=DBUS_OBJM_IFACE, 
                                      signal_name='InterfacesAdded')

        self.bus.add_signal_receiver( self._interfaces_removed_handler,
                                      dbus_interface=DBUS_OBJM_IFACE, 
                                      signal_name='InterfacesRemoved')

        self.bus.add_signal_receiver(self._properties_changed_handler,
                                     dbus_interface=dbus.PROPERTIES_IFACE,
                                     signal_name='PropertiesChanged',
                                     arg0=DEVICE_INTERFACE,
                                     path_keyword='path')

        self.adapters = []
        self.devices = []
        self.adapter = self.Adapter_Interface()
        self.device = self.Device_Interface()
        
   
    class Adapter_Interface:            
        def bind_name(self, hci_name , name):
            pass

    class Device_Interface:

        def register(self, name):
            """discover and pair device"""
            pass

        def is_connected(self, name):
            pass 

        def connect(self, name):
            pass
        def disconnect(self, name):
            pass
    

    def _interfaces_added_handler(self, path, device_info):
        print(path, device_info)

    def _interfaces_removed_handler(self, path, device_info):
        print(path, device_info)

    def _properties_changed_handler(self, interface, changed, invalidated, path):
        print(interface, path)
