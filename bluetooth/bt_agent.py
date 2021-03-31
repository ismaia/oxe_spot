import logging
import sys
import dbus
import os, sys, traceback
import dbus.service
import dbus.mainloop.glib
from gi.repository import GObject

logger = logging.getLogger(name='oxe_bt_agent')


AGENT_INTERFACE = "org.bluez.Agent1"
AGENT_PATH = "/oxe_spot/bt_agent"

UUID_HSP_HS='00001108-0000-1000-8000-00805f9b34fb'
UUID_ADVANCED_AUDIO='0000110d-0000-1000-8000-00805f9b34fb'
UUID_A2DP_SOURCE='0000110a-0000-1000-8000-00805f9b34fb'
UUID_A2DP_SINK='0000110b-0000-1000-8000-00805f9b34fb'

  
class Rejected(dbus.DBusException):
	_dbus_error_name = "org.bluez.Error.Rejected"

class BtAgentService(dbus.service.Object):
	def __init__(self):		
		try:
			bus = dbus.SystemBus()		
			dbus.service.Object.__init__(self, bus , AGENT_PATH)		
			obj = bus.get_object("org.bluez", "/org/bluez")
			manager = dbus.Interface(obj, "org.bluez.AgentManager1")
			manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")	
			manager.RequestDefaultAgent(AGENT_PATH)

			self.authorized_uuids=[UUID_ADVANCED_AUDIO, UUID_HSP_HS, UUID_A2DP_SOURCE, UUID_A2DP_SINK]		
			logger.info("Audio profiles authorized")

		except:
			self._log_exception()

	
	def start(self):
		pass
	
	def stop(self):
		pass


	@dbus.service.method(AGENT_INTERFACE,
					in_signature="", out_signature="")
	def Release(self):
		logger.info("Release")

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="os", out_signature="")
	def AuthorizeService(self, device, uuid):
		logger.info('AuthorizeService [' + str(uuid) + ' => ' + str(device) + ']' )		
		if uuid in self.authorized_uuids:
			logger.info("Service UUID Authorized : " + str(uuid))
			return
		logger.info("Rejecting non authorized Service : " + str(uuid))
		raise Rejected("Connection rejected")

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="o", out_signature="s")
	def RequestPinCode(self, device):
		logger.info('RequestPinCode : ' + str(device))		
		return "0000"

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="o", out_signature="u")
	def RequestPasskey(self, device):
		logger.info('RequestPasskey :' + str(device))		
		return dbus.UInt32('0000')

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="ouq", out_signature="")
	def DisplayPasskey(self, device, passkey, entered):		
		logger.info('DisplayPasskey :' + str(device) + ',' + str(passkey) + ',' + str(entered) )		

	@dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
	def DisplayPinCode(self, device, pincode):
		logger.info('DisplayPinCode :' + str(device) + ',' + str(pincode))

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="ou", out_signature="")
	def RequestConfirmation(self, device, passkey):
		logger.info('RequestConfirmation :' + str(device) + ',' + str(passkey))				

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="o", out_signature="")
	def RequestAuthorization(self, device):		
		logger.info('RequestAuthorization: ' + str(device))

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="", out_signature="")
	def Cancel(self):
		logger.info('Cancel')

	def _log_exception(self):
		ex = str(sys.exc_info()[1])
		tb = sys.exc_info()[-1]
		stk = traceback.extract_tb(tb, 1)
		func_name = stk[0][2]            
		logger.error("Error : " + func_name + ' : ' + ex)

