import struct

from GBOperationMessage import (
    GB_OP_SUCCESS,
    GB_VERSION_MAJOR,
    GB_VERSION_MINOR,
    GB_REQUEST_TYPE_CPORT_SHUTDOWN
)

from GBHandler import GBHandler

GB_CONTROL_TYPE_VERSION = 0x01
GB_CONTROL_TYPE_PROBE_AP = 0x02
GB_CONTROL_TYPE_GET_MANIFEST_SIZE = 0x03
GB_CONTROL_TYPE_GET_MANIFEST = 0x04
GB_CONTROL_TYPE_CONNECTED = 0x05
GB_CONTROL_TYPE_DISCONNECTED = 0x06
GB_CONTROL_TYPE_TIMESYNC_ENABLE = 0x07
GB_CONTROL_TYPE_TIMESYNC_DISABLE = 0x08
GB_CONTROL_TYPE_TIMESYNC_AUTHORITATIVE = 0x09
GB_CONTROL_TYPE_BUNDLE_VERSION = 0x0b
GB_CONTROL_TYPE_DISCONNECTING = 0x0c
GB_CONTROL_TYPE_TIMESYNC_GET_LAST_EVENT = 0x0d
GB_CONTROL_TYPE_MODE_SWITCH = 0x0e
GB_CONTROL_TYPE_BUNDLE_SUSPEND = 0x0f
GB_CONTROL_TYPE_BUNDLE_RESUME = 0x10
GB_CONTROL_TYPE_BUNDLE_DEACTIVATE = 0x11
GB_CONTROL_TYPE_BUNDLE_ACTIVATE = 0x12
GB_CONTROL_TYPE_INTF_SUSPEND_PREPARE = 0x13
GB_CONTROL_TYPE_INTF_DEACTIVATE_PREPARE = 0x14
GB_CONTROL_TYPE_INTF_HIBERNATE_ABORT = 0x15

GB_CONTROL_INTF_PM_OK = 0x00
GB_CONTROL_INTF_PM_BUSY = 0x01
GB_CONTROL_INTF_PM_NA = 0x02

GB_CONTROL_BUNDLE_PM_OK = 0x00
GB_CONTROL_BUNDLE_PM_INVAL = 0x01
GB_CONTROL_BUNDLE_PM_BUSY = 0x02
GB_CONTROL_BUNDLE_PM_FAIL = 0x03
GB_CONTROL_BUNDLE_PM_NA = 0x04

class GBControlHandler(GBHandler):
        
    def __init__(self, sock, manifest):
        GBHandler.__init__(self, sock, GBControlHandler.getHandlers())
        self._manifest = manifest
        self._name = "Control"
    
    def identify(self, t):
        if GB_REQUEST_TYPE_CPORT_SHUTDOWN == t:          return 'GB_REQUEST_TYPE_CPORT_SHUTDOWN         '
        if GB_CONTROL_TYPE_VERSION == t:                 return 'GB_CONTROL_TYPE_VERSION                '
        if GB_CONTROL_TYPE_PROBE_AP == t:                return 'GB_CONTROL_TYPE_PROBE_AP               '
        if GB_CONTROL_TYPE_GET_MANIFEST_SIZE == t:       return 'GB_CONTROL_TYPE_GET_MANIFEST_SIZE      '
        if GB_CONTROL_TYPE_GET_MANIFEST == t:            return 'GB_CONTROL_TYPE_GET_MANIFEST           '
        if GB_CONTROL_TYPE_CONNECTED == t:               return 'GB_CONTROL_TYPE_CONNECTED              '
        if GB_CONTROL_TYPE_DISCONNECTED == t:            return 'GB_CONTROL_TYPE_DISCONNECTED           '
        if GB_CONTROL_TYPE_TIMESYNC_ENABLE == t:         return 'GB_CONTROL_TYPE_TIMESYNC_ENABLE        '
        if GB_CONTROL_TYPE_TIMESYNC_DISABLE == t:        return 'GB_CONTROL_TYPE_TIMESYNC_DISABLE       '
        if GB_CONTROL_TYPE_TIMESYNC_AUTHORITATIVE == t:  return 'GB_CONTROL_TYPE_TIMESYNC_AUTHORITATIVE '
        if GB_CONTROL_TYPE_BUNDLE_VERSION == t:          return 'GB_CONTROL_TYPE_BUNDLE_VERSION         '
        if GB_CONTROL_TYPE_DISCONNECTING == t:           return 'GB_CONTROL_TYPE_DISCONNECTING          '
        if GB_CONTROL_TYPE_TIMESYNC_GET_LAST_EVENT == t: return 'GB_CONTROL_TYPE_TIMESYNC_GET_LAST_EVENT'
        if GB_CONTROL_TYPE_MODE_SWITCH == t:             return 'GB_CONTROL_TYPE_MODE_SWITCH            '
        if GB_CONTROL_TYPE_BUNDLE_SUSPEND == t:          return 'GB_CONTROL_TYPE_BUNDLE_SUSPEND         '
        if GB_CONTROL_TYPE_BUNDLE_RESUME == t:           return 'GB_CONTROL_TYPE_BUNDLE_RESUME          '
        if GB_CONTROL_TYPE_BUNDLE_DEACTIVATE == t:       return 'GB_CONTROL_TYPE_BUNDLE_DEACTIVATE      '
        if GB_CONTROL_TYPE_BUNDLE_ACTIVATE == t:         return 'GB_CONTROL_TYPE_BUNDLE_ACTIVATE        '
        if GB_CONTROL_TYPE_INTF_SUSPEND_PREPARE == t:    return 'GB_CONTROL_TYPE_INTF_SUSPEND_PREPARE   '
        if GB_CONTROL_TYPE_INTF_DEACTIVATE_PREPARE == t: return 'GB_CONTROL_TYPE_INTF_DEACTIVATE_PREPARE'
        if GB_CONTROL_TYPE_INTF_HIBERNATE_ABORT == t:    return 'GB_CONTROL_TYPE_INTF_HIBERNATE_ABORT   '
        return None
    
    def handle_CPORT_SHUTDOWN( self, msg ):
        return msg.response( GB_OP_SUCCESS )

    def handle_VERSION( self, msg ):
        payload = struct.pack( 'BB', GB_VERSION_MAJOR, GB_VERSION_MINOR )
        resp = msg.response( GB_OP_SUCCESS, payload )
        return resp

    def handle_PROBE_AP( self, msg ):
        return msg.response( GB_OP_SUCCESS )

    def handle_GET_MANIFEST_SIZE( self, msg ):
        sz = len( self._manifest )
        payload = struct.pack( '<H', sz )
        resp = msg.response( GB_OP_SUCCESS, payload )
        return resp
        
    def handle_GET_MANIFEST( self, msg ):
        payload = buffer( self._manifest )
        resp = msg.response( GB_OP_SUCCESS, payload )
        return resp
        
    def handle_CONNECTED( self, msg ):
        return msg.response( GB_OP_SUCCESS )

    def handle_DISCONNECTED( self, msg ):
        return msg.response( GB_OP_SUCCESS )

    def handle_TIMESYNC_ENABLE( self, msg ):
        return msg.response( GB_OP_SUCCESS )

    def handle_TIMESYNC_DISABLE( self, msg ):
        return msg.response( GB_OP_SUCCESS )

    def handle_TIMESYNC_AUTHORITATIVE( self, msg ):
        return msg.response( GB_OP_SUCCESS )
        
    def handle_BUNDLE_VERSION( self, msg ):
        return msg.response( GB_OP_SUCCESS )
        
    def handle_DISCONNECTING( self, msg ):
        return msg.response( GB_OP_SUCCESS )
        
    def handle_TIMESYNC_GET_LAST_EVENT( self, msg ):
        return msg.response( GB_OP_SUCCESS )
        
    def handle_MODE_SWITCH( self, msg ):
        return msg.response( GB_OP_SUCCESS )
        
    def handle_BUNDLE_SUSPEND( self, msg ):
        payload = struct.pack( 'B', GB_CONTROL_BUNDLE_PM_OK )
        return msg.response( GB_OP_SUCCESS, payload )
        
    def handle_BUNDLE_RESUME( self, msg ):
        payload = struct.pack( 'B', GB_CONTROL_BUNDLE_PM_OK )
        return msg.response( GB_OP_SUCCESS, payload )
        
    def handle_BUNDLE_DEACTIVATE( self, msg ):
        payload = struct.pack( 'B', GB_CONTROL_BUNDLE_PM_OK )
        return msg.response( GB_OP_SUCCESS, payload )
        
    def handle_BUNDLE_ACTIVATE( self, msg ):
        payload = struct.pack( 'B', GB_CONTROL_BUNDLE_PM_OK )
        return msg.response( GB_OP_SUCCESS, payload )
        
    def handle_INTF_SUSPEND_PREPARE( self, msg ):
        payload = struct.pack( 'B', GB_CONTROL_INTF_PM_OK )
        return msg.response( GB_OP_SUCCESS, payload )
        
    def handle_INTF_DEACTIVATE_PREPARE( self, msg ):
        payload = struct.pack( 'B', GB_CONTROL_INTF_PM_OK )
        return msg.response( GB_OP_SUCCESS, payload )
        
    def handle_INTF_HIBERNATE_ABORT( self, msg ):
        return msg.response( GB_OP_SUCCESS )
    
    @staticmethod
    def getHandlers():
        hdlrs = {}        
        hdlrs[ GB_REQUEST_TYPE_CPORT_SHUTDOWN ] = GBControlHandler.handle_CPORT_SHUTDOWN
        hdlrs[ GB_CONTROL_TYPE_VERSION ] = GBControlHandler.handle_VERSION
        hdlrs[ GB_CONTROL_TYPE_PROBE_AP ] = GBControlHandler.handle_PROBE_AP
        hdlrs[ GB_CONTROL_TYPE_GET_MANIFEST_SIZE ] = GBControlHandler.handle_GET_MANIFEST_SIZE
        hdlrs[ GB_CONTROL_TYPE_GET_MANIFEST ] = GBControlHandler.handle_GET_MANIFEST
        hdlrs[ GB_CONTROL_TYPE_CONNECTED ] = GBControlHandler.handle_CONNECTED
        hdlrs[ GB_CONTROL_TYPE_DISCONNECTED ] = GBControlHandler.handle_DISCONNECTED
        hdlrs[ GB_CONTROL_TYPE_TIMESYNC_ENABLE ] = GBControlHandler.handle_TIMESYNC_ENABLE
        hdlrs[ GB_CONTROL_TYPE_TIMESYNC_DISABLE ] = GBControlHandler.handle_TIMESYNC_DISABLE
        hdlrs[ GB_CONTROL_TYPE_TIMESYNC_AUTHORITATIVE ] = GBControlHandler.handle_TIMESYNC_AUTHORITATIVE
        hdlrs[ GB_CONTROL_TYPE_BUNDLE_VERSION ] = GBControlHandler.handle_BUNDLE_VERSION
        hdlrs[ GB_CONTROL_TYPE_DISCONNECTING ] = GBControlHandler.handle_DISCONNECTING
        hdlrs[ GB_CONTROL_TYPE_TIMESYNC_GET_LAST_EVENT ] = GBControlHandler.handle_TIMESYNC_GET_LAST_EVENT
        hdlrs[ GB_CONTROL_TYPE_MODE_SWITCH ] = GBControlHandler.handle_MODE_SWITCH
        hdlrs[ GB_CONTROL_TYPE_BUNDLE_SUSPEND ] = GBControlHandler.handle_BUNDLE_SUSPEND
        hdlrs[ GB_CONTROL_TYPE_BUNDLE_RESUME ] = GBControlHandler.handle_BUNDLE_RESUME
        hdlrs[ GB_CONTROL_TYPE_BUNDLE_DEACTIVATE ] = GBControlHandler.handle_BUNDLE_DEACTIVATE
        hdlrs[ GB_CONTROL_TYPE_BUNDLE_ACTIVATE ] = GBControlHandler.handle_BUNDLE_ACTIVATE
        hdlrs[ GB_CONTROL_TYPE_INTF_SUSPEND_PREPARE ] = GBControlHandler.handle_INTF_SUSPEND_PREPARE
        hdlrs[ GB_CONTROL_TYPE_INTF_DEACTIVATE_PREPARE ] = GBControlHandler.handle_INTF_DEACTIVATE_PREPARE
        hdlrs[ GB_CONTROL_TYPE_INTF_HIBERNATE_ABORT ] = GBControlHandler.handle_INTF_HIBERNATE_ABORT
        return hdlrs
