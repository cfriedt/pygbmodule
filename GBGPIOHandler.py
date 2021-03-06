import socket
import struct

from GBOperationMessage import (
    GB_OP_SUCCESS,
    GB_OP_RESPONSE,
    GB_VERSION_MAJOR,
    GB_VERSION_MINOR,
    GB_REQUEST_TYPE_CPORT_SHUTDOWN
)

from GBHandler import GBHandler

GB_GPIO_TYPE_LINE_COUNT = 0x02
GB_GPIO_TYPE_ACTIVATE = 0x03
GB_GPIO_TYPE_DEACTIVATE = 0x04
GB_GPIO_TYPE_GET_DIRECTION = 0x05
GB_GPIO_TYPE_DIRECTION_IN = 0x06
GB_GPIO_TYPE_DIRECTION_OUT = 0x07
GB_GPIO_TYPE_GET_VALUE = 0x08
GB_GPIO_TYPE_SET_VALUE = 0x09
GB_GPIO_TYPE_SET_DEBOUNCE = 0x0a
GB_GPIO_TYPE_IRQ_TYPE = 0x0b
GB_GPIO_TYPE_IRQ_MASK = 0x0c
GB_GPIO_TYPE_IRQ_UNMASK = 0x0d
GB_GPIO_TYPE_IRQ_EVENT = 0x0e

GB_GPIO_IRQ_TYPE_NONE = 0x00
GB_GPIO_IRQ_TYPE_EDGE_RISING = 0x01
GB_GPIO_IRQ_TYPE_EDGE_FALLING = 0x02
GB_GPIO_IRQ_TYPE_EDGE_BOTH = 0x03
GB_GPIO_IRQ_TYPE_LEVEL_HIGH = 0x04
GB_GPIO_IRQ_TYPE_LEVEL_LOW = 0x08

class GBGPIOHandler(GBHandler):
        
    def __init__(self, sock, ngpio = 1 ):
        GBHandler.__init__(self, sock, GBGPIOHandler.getHandlers())
        self._name = "GPIO"
        self._ngpio = ngpio
        self._gpio_data       = [0]     * ngpio
        self._gpio_dir_input  = [True]  * ngpio
        self._gpio_irqt       = [0]     * ngpio
        self._gpio_mask       = [False] * ngpio
        self._gpio_debounce   = [0]     * ngpio
        
    def identify( self, t ):
        if GB_REQUEST_TYPE_CPORT_SHUTDOWN == t: return 'GB_REQUEST_TYPE_CPORT_SHUTDOWN' 
        if GB_GPIO_TYPE_LINE_COUNT == t:    return 'GB_GPIO_TYPE_LINE_COUNT   '
        if GB_GPIO_TYPE_ACTIVATE == t:      return 'GB_GPIO_TYPE_ACTIVATE     '
        if GB_GPIO_TYPE_DEACTIVATE == t:    return 'GB_GPIO_TYPE_DEACTIVATE   '
        if GB_GPIO_TYPE_GET_DIRECTION == t: return 'GB_GPIO_TYPE_GET_DIRECTION'
        if GB_GPIO_TYPE_DIRECTION_IN == t:  return 'GB_GPIO_TYPE_DIRECTION_IN '
        if GB_GPIO_TYPE_DIRECTION_OUT == t: return 'GB_GPIO_TYPE_DIRECTION_OUT'
        if GB_GPIO_TYPE_GET_VALUE == t:     return 'GB_GPIO_TYPE_GET_VALUE    '
        if GB_GPIO_TYPE_SET_VALUE == t:     return 'GB_GPIO_TYPE_SET_VALUE    '
        if GB_GPIO_TYPE_SET_DEBOUNCE == t:  return 'GB_GPIO_TYPE_SET_DEBOUNCE '
        if GB_GPIO_TYPE_IRQ_TYPE == t:      return 'GB_GPIO_TYPE_IRQ_TYPE     '
        if GB_GPIO_TYPE_IRQ_MASK == t:      return 'GB_GPIO_TYPE_IRQ_MASK     '
        if GB_GPIO_TYPE_IRQ_UNMASK == t:    return 'GB_GPIO_TYPE_IRQ_UNMASK   '
        if GB_GPIO_TYPE_IRQ_EVENT == t:     return 'GB_GPIO_TYPE_IRQ_EVENT    '
        return None

    def handle_CPORT_SHUTDOWN(self, msg):
        return msg.response( GB_OP_SUCCESS )

    def handle_LINE_COUNT( self, msg ):
        payload = struct.pack( 'B', self._ngpio - 1 )
        return msg.response( GB_OP_SUCCESS, payload );
 
    def handle_ACTIVATE( self, msg ):
        return msg.response( GB_OP_SUCCESS )
 
    def handle_DEACTIVATE( self, msg ):
        return msg.response( GB_OP_SUCCESS )
 
    def handle_GET_DIRECTION( self, msg ):
        (which,) = struct.unpack( 'B', msg.payload() )
        payload = struct.pack( 'B', self._gpio_dir_input[ which ] )
        return msg.response( GB_OP_SUCCESS, payload )
 
    def handle_DIRECTION_IN( self, msg ):
        (which,) = struct.unpack( 'B', msg.payload() )
        self._gpio_dir_input[ which ] = True
        return msg.response( GB_OP_SUCCESS )
 
    def handle_DIRECTION_OUT( self, msg ):
        which, val = struct.unpack( 'BB', msg.payload() )
        self._gpio_dir_input[ which ] = False
        self._gpio_data[ which ] = val
        return msg.response( GB_OP_SUCCESS )
 
    def handle_GET_VALUE( self, msg ):
        (which,) = struct.unpack( 'B', msg.payload() )
        payload = struct.pack( 'B', self._gpio_data[ which ] )
        return msg.response( GB_OP_SUCCESS, payload )
 
    def handle_SET_VALUE( self, msg ):
        which, val = struct.unpack( 'BB', msg.payload() )
        self._gpio_dir_input[ which ] = False
        self._gpio_data[ which ] = val
        return msg.response( GB_OP_SUCCESS )
 
    def handle_SET_DEBOUNCE( self, msg ):
        which, val = struct.unpack( '<BH', msg.payload() )
        self._gpio_debounce[ which ] = val
        return msg.response( GB_OP_SUCCESS )
 
    def handle_IRQ_TYPE( self, msg ):
        which, val = struct.unpack( 'BB', msg.payload() )
        self._gpio_irqt[ which ] = val
        return msg.response( GB_OP_SUCCESS )
 
    def handle_IRQ_MASK( self, msg ):
        (which,) = struct.unpack( 'B', msg.payload() )
        self._gpio_mask[ which ] = True
        return msg.response( GB_OP_SUCCESS )
 
    def handle_IRQ_UNMASK( self, msg ):
        (which,) = struct.unpack( 'B', msg.payload() )
        self._gpio_mask[ which ] = False
        return msg.response( GB_OP_SUCCESS )
 
    def handle_IRQ_EVENT_resp( self, msg ):
        if GB_OP_SUCCESS == msg.result():
            print('{}: interrupt handled'.format( self._name ) )
        if GB_OP_SUCCESS == msg.result():
            print('{}: interrupt not handled'.format( self._name ) )
        pass

    @staticmethod
    def getHandlers():
        hdlrs = {}
        hdlrs[ GB_REQUEST_TYPE_CPORT_SHUTDOWN ] = GBGPIOHandler.handle_CPORT_SHUTDOWN
        hdlrs[ GB_GPIO_TYPE_LINE_COUNT ] = GBGPIOHandler.handle_LINE_COUNT
        hdlrs[ GB_GPIO_TYPE_ACTIVATE ] = GBGPIOHandler.handle_ACTIVATE
        hdlrs[ GB_GPIO_TYPE_DEACTIVATE ] = GBGPIOHandler.handle_DEACTIVATE
        hdlrs[ GB_GPIO_TYPE_GET_DIRECTION ] = GBGPIOHandler.handle_GET_DIRECTION
        hdlrs[ GB_GPIO_TYPE_DIRECTION_IN ] = GBGPIOHandler.handle_DIRECTION_IN
        hdlrs[ GB_GPIO_TYPE_DIRECTION_OUT ] = GBGPIOHandler.handle_DIRECTION_OUT
        hdlrs[ GB_GPIO_TYPE_GET_VALUE ] = GBGPIOHandler.handle_GET_VALUE
        hdlrs[ GB_GPIO_TYPE_SET_VALUE ] = GBGPIOHandler.handle_SET_VALUE
        hdlrs[ GB_GPIO_TYPE_SET_DEBOUNCE ] = GBGPIOHandler.handle_SET_DEBOUNCE
        hdlrs[ GB_GPIO_TYPE_IRQ_TYPE ] = GBGPIOHandler.handle_IRQ_TYPE
        hdlrs[ GB_GPIO_TYPE_IRQ_MASK ] = GBGPIOHandler.handle_IRQ_MASK
        hdlrs[ GB_GPIO_TYPE_IRQ_UNMASK ] = GBGPIOHandler.handle_IRQ_UNMASK
        hdlrs[ GB_GPIO_TYPE_IRQ_EVENT | GB_OP_RESPONSE ] = GBGPIOHandler.handle_IRQ_EVENT_resp
        return hdlrs
