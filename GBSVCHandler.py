import struct

from GBOperationMessage import (
    GBOperationMessage,
    GB_OP_SUCCESS,
    GB_VERSION_MAJOR,
    GB_VERSION_MINOR,
    GB_REQUEST_TYPE_CPORT_SHUTDOWN
, GB_OP_RESPONSE)

from GBHandler import GBHandler
from GBNetlinkAdapter import GBNetlinkAdapter

GB_SVC_TYPE_PROTOCOL_VERSION = 0x01
GB_SVC_TYPE_SVC_HELLO = 0x02
GB_SVC_TYPE_INTF_DEVICE_ID = 0x03
GB_SVC_TYPE_INTF_RESET = 0x06
GB_SVC_TYPE_CONN_CREATE = 0x07
GB_SVC_TYPE_CONN_DESTROY = 0x08
GB_SVC_TYPE_DME_PEER_GET = 0x09
GB_SVC_TYPE_DME_PEER_SET = 0x0a
GB_SVC_TYPE_ROUTE_CREATE = 0x0b
GB_SVC_TYPE_ROUTE_DESTROY = 0x0c
GB_SVC_TYPE_TIMESYNC_ENABLE = 0x0d
GB_SVC_TYPE_TIMESYNC_DISABLE = 0x0e
GB_SVC_TYPE_TIMESYNC_AUTHORITATIVE = 0x0f
GB_SVC_TYPE_INTF_SET_PWRM = 0x10
GB_SVC_TYPE_INTF_EJECT = 0x11
GB_SVC_TYPE_PING = 0x13
GB_SVC_TYPE_PWRMON_RAIL_COUNT_GET = 0x14
GB_SVC_TYPE_PWRMON_RAIL_NAMES_GET = 0x15
GB_SVC_TYPE_PWRMON_SAMPLE_GET = 0x16
GB_SVC_TYPE_PWRMON_INTF_SAMPLE_GET = 0x17
GB_SVC_TYPE_TIMESYNC_WAKE_PINS_ACQUIRE = 0x18
GB_SVC_TYPE_TIMESYNC_WAKE_PINS_RELEASE = 0x19
GB_SVC_TYPE_TIMESYNC_PING = 0x1a
GB_SVC_TYPE_MODULE_INSERTED = 0x1f
GB_SVC_TYPE_MODULE_REMOVED = 0x20
GB_SVC_TYPE_INTF_VSYS_ENABLE = 0x21
GB_SVC_TYPE_INTF_VSYS_DISABLE = 0x22
GB_SVC_TYPE_INTF_REFCLK_ENABLE = 0x23
GB_SVC_TYPE_INTF_REFCLK_DISABLE = 0x24
GB_SVC_TYPE_INTF_UNIPRO_ENABLE = 0x25
GB_SVC_TYPE_INTF_UNIPRO_DISABLE = 0x26
GB_SVC_TYPE_INTF_ACTIVATE = 0x27
GB_SVC_TYPE_INTF_RESUME = 0x28
GB_SVC_TYPE_INTF_MAILBOX_EVENT = 0x29
GB_SVC_TYPE_INTF_OOPS = 0x2a

GB_SVC_OP_SUCCESS = 0x00
GB_SVC_OP_UNKNOWN_ERROR = 0x01
GB_SVC_INTF_NOT_DETECTED = 0x02
GB_SVC_INTF_NO_UPRO_LINK = 0x03
GB_SVC_INTF_UPRO_NOT_DOWN = 0x04
GB_SVC_INTF_UPRO_NOT_HIBERNATED = 0x05
GB_SVC_INTF_NO_V_SYS = 0x06
GB_SVC_INTF_V_CHG = 0x07
GB_SVC_INTF_WAKE_BUSY = 0x08
GB_SVC_INTF_NO_REFCLK = 0x09
GB_SVC_INTF_RELEASING = 0x0a
GB_SVC_INTF_NO_ORDER = 0x0b
GB_SVC_INTF_MBOX_SET = 0x0c
GB_SVC_INTF_BAD_MBOX = 0x0d
GB_SVC_INTF_OP_TIMEOUT = 0x0e
GB_SVC_PWRMON_OP_NOT_PRESENT = 0x0f

class GBSVCHandler(GBHandler):
        
    def __init__(self, sock):
        GBHandler.__init__(self, -1, GBSVCHandler.getHandlers())
        self._name = "SVC"
        self._client_sock_is_static = True
        self._client_sock =  sock
    
    def identify(self, t):
        if GB_REQUEST_TYPE_CPORT_SHUTDOWN == t:         return 'GB_REQUEST_TYPE_CPORT_SHUTDOWN        '
        if GB_SVC_TYPE_PROTOCOL_VERSION == t:           return 'GB_SVC_TYPE_PROTOCOL_VERSION          '
        if GB_SVC_TYPE_SVC_HELLO == t:                  return 'GB_SVC_TYPE_SVC_HELLO                 '
        if GB_SVC_TYPE_INTF_DEVICE_ID == t:             return 'GB_SVC_TYPE_INTF_DEVICE_ID            '
        if GB_SVC_TYPE_INTF_RESET == t:                 return 'GB_SVC_TYPE_INTF_RESET                '
        if GB_SVC_TYPE_CONN_CREATE == t:                return 'GB_SVC_TYPE_CONN_CREATE               '
        if GB_SVC_TYPE_CONN_DESTROY == t:               return 'GB_SVC_TYPE_CONN_DESTROY              '
        if GB_SVC_TYPE_DME_PEER_GET == t:               return 'GB_SVC_TYPE_DME_PEER_GET              '
        if GB_SVC_TYPE_DME_PEER_SET == t:               return 'GB_SVC_TYPE_DME_PEER_SET              '
        if GB_SVC_TYPE_ROUTE_CREATE == t:               return 'GB_SVC_TYPE_ROUTE_CREATE              '
        if GB_SVC_TYPE_ROUTE_DESTROY == t:              return 'GB_SVC_TYPE_ROUTE_DESTROY             '
        if GB_SVC_TYPE_TIMESYNC_ENABLE == t:            return 'GB_SVC_TYPE_TIMESYNC_ENABLE           '
        if GB_SVC_TYPE_TIMESYNC_DISABLE == t:           return 'GB_SVC_TYPE_TIMESYNC_DISABLE          '
        if GB_SVC_TYPE_TIMESYNC_AUTHORITATIVE == t:     return 'GB_SVC_TYPE_TIMESYNC_AUTHORITATIVE    '
        if GB_SVC_TYPE_INTF_SET_PWRM == t:              return 'GB_SVC_TYPE_INTF_SET_PWRM             '
        if GB_SVC_TYPE_INTF_EJECT == t:                 return 'GB_SVC_TYPE_INTF_EJECT                '
        if GB_SVC_TYPE_PING == t:                       return 'GB_SVC_TYPE_PING                      '
        if GB_SVC_TYPE_PWRMON_RAIL_COUNT_GET == t:      return 'GB_SVC_TYPE_PWRMON_RAIL_COUNT_GET     '
        if GB_SVC_TYPE_PWRMON_RAIL_NAMES_GET == t:      return 'GB_SVC_TYPE_PWRMON_RAIL_NAMES_GET     '
        if GB_SVC_TYPE_PWRMON_SAMPLE_GET == t:          return 'GB_SVC_TYPE_PWRMON_SAMPLE_GET         '
        if GB_SVC_TYPE_PWRMON_INTF_SAMPLE_GET == t:     return 'GB_SVC_TYPE_PWRMON_INTF_SAMPLE_GET    '
        if GB_SVC_TYPE_TIMESYNC_WAKE_PINS_ACQUIRE == t: return 'GB_SVC_TYPE_TIMESYNC_WAKE_PINS_ACQUIRE'
        if GB_SVC_TYPE_TIMESYNC_WAKE_PINS_RELEASE == t: return 'GB_SVC_TYPE_TIMESYNC_WAKE_PINS_RELEASE'
        if GB_SVC_TYPE_TIMESYNC_PING == t:              return 'GB_SVC_TYPE_TIMESYNC_PING             '
        if GB_SVC_TYPE_MODULE_INSERTED == t:            return 'GB_SVC_TYPE_MODULE_INSERTED           '
        if GB_SVC_TYPE_MODULE_REMOVED == t:             return 'GB_SVC_TYPE_MODULE_REMOVED            '
        if GB_SVC_TYPE_INTF_VSYS_ENABLE == t:           return 'GB_SVC_TYPE_INTF_VSYS_ENABLE          '
        if GB_SVC_TYPE_INTF_VSYS_DISABLE == t:          return 'GB_SVC_TYPE_INTF_VSYS_DISABLE         '
        if GB_SVC_TYPE_INTF_REFCLK_ENABLE == t:         return 'GB_SVC_TYPE_INTF_REFCLK_ENABLE        '
        if GB_SVC_TYPE_INTF_REFCLK_DISABLE == t:        return 'GB_SVC_TYPE_INTF_REFCLK_DISABLE       '
        if GB_SVC_TYPE_INTF_UNIPRO_ENABLE == t:         return 'GB_SVC_TYPE_INTF_UNIPRO_ENABLE        '
        if GB_SVC_TYPE_INTF_UNIPRO_DISABLE == t:        return 'GB_SVC_TYPE_INTF_UNIPRO_DISABLE       '
        if GB_SVC_TYPE_INTF_ACTIVATE == t:              return 'GB_SVC_TYPE_INTF_ACTIVATE             '
        if GB_SVC_TYPE_INTF_RESUME == t:                return 'GB_SVC_TYPE_INTF_RESUME               '
        if GB_SVC_TYPE_INTF_MAILBOX_EVENT == t:         return 'GB_SVC_TYPE_INTF_MAILBOX_EVENT        '
        if GB_SVC_TYPE_INTF_OOPS == t:                  return 'GB_SVC_TYPE_INTF_OOPS                 '
        return None

    def connectToAP(self):
        self.PROTOCOL_VERSION()

    def handler_CPORT_SHUTDOWN(self, req):
        return req.response( GB_OP_SUCCESS )

    def PROTOCOL_VERSION(self):
        operation_id = self._operation_id
        self._operation_id = self._operation_id + 1

        major = GB_VERSION_MAJOR
        minor = GB_VERSION_MINOR
        payload = struct.pack( 'BB', major, minor )
        
        protocol_version_msg = GBOperationMessage( ( operation_id, GB_SVC_TYPE_PROTOCOL_VERSION, payload ) )
        
        self.send( protocol_version_msg )

    # PROTOCOL_VERSION is sent by the SVC to the AP, so this is a response handler
    def handler_PROTOCOL_VERSION( self, resp ):

        result = resp.result()        
        if GB_OP_SUCCESS != result:
            raise IOError( 'AP response to PROTOCOL_VERION was {}'.format( result ) )

        payload = resp.payload()
        major = ord( payload[ 0 ] )
        minor = ord( payload[ 1 ] )
        
        if not( GB_VERSION_MAJOR == major and GB_VERSION_MINOR == minor ):
            raise IOError( 'unexpected AP response to PROTOCOL_VERSION: {}.{}'.format( major, minor ) )
        
        print( 'AP PROTOCOL_VERION: {}.{}'.format( major, minor ) )

        self.SVC_HELLO()

    def SVC_HELLO(self):

        operation_id = self._operation_id
        self._operation_id = self._operation_id + 1

        ENDO_ID = 0x4755
        AP_INTF_ID = 0

        endo_id = ENDO_ID;
        interface_id = AP_INTF_ID;
        
        payload = struct.pack( '<HB', endo_id, interface_id )
        
        svc_hello_msg = GBOperationMessage( ( operation_id, GB_SVC_TYPE_SVC_HELLO, payload ) )
        
        self.send( svc_hello_msg )

    # PROTOCOL_VERSION is sent by the SVC to the AP, so this is a response handler
    def handler_SVC_HELLO( self, resp ):
        
        result = resp.result()        
        if GB_OP_SUCCESS != result:
            raise IOError( 'AP response to PROTOCOL_VERION was {}'.format( result ) )
        
        print( 'received SVC_HELLO response' )
    
    def handler_INTF_DEVICE_ID( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_RESET( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_CONN_CREATE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_CONN_DESTROY( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_DME_PEER_GET( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_DME_PEER_SET( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_ROUTE_CREATE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_ROUTE_DESTROY( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_TIMESYNC_ENABLE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_TIMESYNC_DISABLE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_TIMESYNC_AUTHORITATIVE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_SET_PWRM( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_EJECT( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_PING( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_PWRMON_RAIL_COUNT_GET( self, req ):        
        payload = struct.pack( 'B', 1 )
        resp = req.response( GB_OP_SUCCESS, payload )
        return resp
    
    def handler_PWRMON_RAIL_NAMES_GET( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_PWRMON_SAMPLE_GET( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_PWRMON_INTF_SAMPLE_GET( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_TIMESYNC_WAKE_PINS_ACQUIRE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_TIMESYNC_WAKE_PINS_RELEASE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_TIMESYNC_PING( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_MODULE_INSERTED( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_MODULE_REMOVED( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_VSYS_ENABLE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_VSYS_DISABLE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_REFCLK_ENABLE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_REFCLK_DISABLE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_UNIPRO_ENABLE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_UNIPRO_DISABLE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_ACTIVATE( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_RESUME( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_MAILBOX_EVENT( self, req ):
        return req.response( GB_OP_SUCCESS )
    
    def handler_INTF_OOPS( self, req ):
        return req.response( GB_OP_SUCCESS )

    @staticmethod
    def getHandlers():
        hdlrs = {}
        hdlrs[ GB_REQUEST_TYPE_CPORT_SHUTDOWN ] = GBSVCHandler.handler_CPORT_SHUTDOWN
        hdlrs[ GB_SVC_TYPE_PROTOCOL_VERSION | GB_OP_RESPONSE] = GBSVCHandler.handler_PROTOCOL_VERSION
        hdlrs[ GB_SVC_TYPE_SVC_HELLO | GB_OP_RESPONSE] = GBSVCHandler.handler_SVC_HELLO
        hdlrs[ GB_SVC_TYPE_INTF_DEVICE_ID ] = GBSVCHandler.handler_INTF_DEVICE_ID
        hdlrs[ GB_SVC_TYPE_INTF_RESET ] = GBSVCHandler.handler_INTF_RESET
        hdlrs[ GB_SVC_TYPE_CONN_CREATE ] = GBSVCHandler.handler_CONN_CREATE
        hdlrs[ GB_SVC_TYPE_CONN_DESTROY ] = GBSVCHandler.handler_CONN_DESTROY
        hdlrs[ GB_SVC_TYPE_DME_PEER_GET ] = GBSVCHandler.handler_DME_PEER_GET
        hdlrs[ GB_SVC_TYPE_DME_PEER_SET ] = GBSVCHandler.handler_DME_PEER_SET
        hdlrs[ GB_SVC_TYPE_ROUTE_CREATE ] = GBSVCHandler.handler_ROUTE_CREATE
        hdlrs[ GB_SVC_TYPE_ROUTE_DESTROY ] = GBSVCHandler.handler_ROUTE_DESTROY
        hdlrs[ GB_SVC_TYPE_TIMESYNC_ENABLE ] = GBSVCHandler.handler_TIMESYNC_ENABLE
        hdlrs[ GB_SVC_TYPE_TIMESYNC_DISABLE ] = GBSVCHandler.handler_TIMESYNC_DISABLE
        hdlrs[ GB_SVC_TYPE_TIMESYNC_AUTHORITATIVE ] = GBSVCHandler.handler_TIMESYNC_AUTHORITATIVE
        hdlrs[ GB_SVC_TYPE_INTF_SET_PWRM ] = GBSVCHandler.handler_INTF_SET_PWRM
        hdlrs[ GB_SVC_TYPE_INTF_EJECT ] = GBSVCHandler.handler_INTF_EJECT
        hdlrs[ GB_SVC_TYPE_PING ] = GBSVCHandler.handler_PING
        hdlrs[ GB_SVC_TYPE_PWRMON_RAIL_COUNT_GET ] = GBSVCHandler.handler_PWRMON_RAIL_COUNT_GET
        hdlrs[ GB_SVC_TYPE_PWRMON_RAIL_NAMES_GET ] = GBSVCHandler.handler_PWRMON_RAIL_NAMES_GET
        hdlrs[ GB_SVC_TYPE_PWRMON_SAMPLE_GET ] = GBSVCHandler.handler_PWRMON_SAMPLE_GET
        hdlrs[ GB_SVC_TYPE_PWRMON_INTF_SAMPLE_GET ] = GBSVCHandler.handler_PWRMON_INTF_SAMPLE_GET
        hdlrs[ GB_SVC_TYPE_TIMESYNC_WAKE_PINS_ACQUIRE ] = GBSVCHandler.handler_TIMESYNC_WAKE_PINS_ACQUIRE
        hdlrs[ GB_SVC_TYPE_TIMESYNC_WAKE_PINS_RELEASE ] = GBSVCHandler.handler_TIMESYNC_WAKE_PINS_RELEASE
        hdlrs[ GB_SVC_TYPE_TIMESYNC_PING ] = GBSVCHandler.handler_TIMESYNC_PING
        hdlrs[ GB_SVC_TYPE_MODULE_INSERTED ] = GBSVCHandler.handler_MODULE_INSERTED
        hdlrs[ GB_SVC_TYPE_MODULE_REMOVED ] = GBSVCHandler.handler_MODULE_REMOVED
        hdlrs[ GB_SVC_TYPE_INTF_VSYS_ENABLE ] = GBSVCHandler.handler_INTF_VSYS_ENABLE
        hdlrs[ GB_SVC_TYPE_INTF_VSYS_DISABLE ] = GBSVCHandler.handler_INTF_VSYS_DISABLE
        hdlrs[ GB_SVC_TYPE_INTF_REFCLK_ENABLE ] = GBSVCHandler.handler_INTF_REFCLK_ENABLE
        hdlrs[ GB_SVC_TYPE_INTF_REFCLK_DISABLE ] = GBSVCHandler.handler_INTF_REFCLK_DISABLE
        hdlrs[ GB_SVC_TYPE_INTF_UNIPRO_ENABLE ] = GBSVCHandler.handler_INTF_UNIPRO_ENABLE
        hdlrs[ GB_SVC_TYPE_INTF_UNIPRO_DISABLE ] = GBSVCHandler.handler_INTF_UNIPRO_DISABLE
        hdlrs[ GB_SVC_TYPE_INTF_ACTIVATE ] = GBSVCHandler.handler_INTF_ACTIVATE
        hdlrs[ GB_SVC_TYPE_INTF_RESUME ] = GBSVCHandler.handler_INTF_RESUME
        hdlrs[ GB_SVC_TYPE_INTF_MAILBOX_EVENT ] = GBSVCHandler.handler_INTF_MAILBOX_EVENT
        hdlrs[ GB_SVC_TYPE_INTF_OOPS ] = GBSVCHandler.handler_INTF_OOPS
        return hdlrs

    # XXX: shouldn't need to do this. GBSwitch should take care of all routing
    def missingHandler(self, msg):
        print( '{}: should route: {}'.format( self._name, msg ) )
        
        if not msg.isResponse():
            resp = msg.response(GBOperationMessage.GB_OP_PROTOCOL_BAD)
            self.send( resp )
