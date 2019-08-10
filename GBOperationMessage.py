import struct

GB_SVC_DEVICE_ID_SVC = 0
GB_SVC_DEVICE_ID_AP = 1
GB_SVC_DEVICE_ID_MIN = 2
GB_SVC_DEVICE_ID_MAX = 31

GB_SVC_CPORT_ID = 0
GB_CONTROL_BUNDLE_ID = 0
GB_CONTROL_CPORT_ID = 0

GB_VERSION_MAJOR = 0x00
GB_VERSION_MINOR = 0x01

GB_OP_SUCCESS = 0x00
GB_OP_INTERRUPTED = 0x01
GB_OP_TIMEOUT = 0x02
GB_OP_NO_MEMORY = 0x03
GB_OP_PROTOCOL_BAD = 0x04
GB_OP_OVERFLOW = 0x05
GB_OP_INVALID = 0x06
GB_OP_RETRY = 0x07
GB_OP_NONEXISTENT = 0x08
GB_OP_INVALID_STATE = 0x09
GB_OP_UNKNOWN_ERROR = 0x0e
GB_OP_INTERNAL = 0xff

GB_OP_RESPONSE = 0x80

GB_REQUEST_TYPE_CPORT_SHUTDOWN = 0x00

class GBOperationMessage(object):
    def __init__(self, data = None ):
        if data is None:
            data = struct.pack( '<HHBBxx', 0, 0, 0xff, 0 )
            return
        
        if isinstance( data, str ):
            data = buffer( data )
        
        if isinstance( data, tuple ):

            if len( data ) == 2:
                # A REQUEST (no payload)
                self._operation_id = data[ 0 ]
                self._type = data[ 1 ]
                self._result = 0
                self._payload = None
                self._size = 8
                return
                
            if len( data ) == 3:
                # A REQUEST
                self._operation_id = data[ 0 ]
                self._type = data[ 1 ]
                self._result = 0
                self._payload = data[ 2 ]
                self._size = 8 + len( self._payload )
                return
                
            if len( data ) == 4:
                # A RESPONSE
                self._operation_id = data[ 0 ]
                self._type = data[ 1 ] | GB_OP_RESPONSE
                self._result = data[ 2 ]
                self._payload = data[ 3 ]
                self._size = 8 + len( self._payload )
                return
            
            raise ValueError( 'unsupported tuple length {0}'.format( len( data ) ) )

        if isinstance( data, buffer ):
            x = struct.unpack( '<HHBBxx', data )
            self._size = x[ 0 ]
            self._operation_id = x[ 1 ]
            self._type = x[ 2 ]
            self._result = x[ 3 ]
            self._payload = None
            
            if len( data ) > 8:
                self._payload = data[ 8: ]
            
#             if len( data ) != self._size:
#                 raise ValueError( "corrupt packet (size: {0}, len: {1})".format( self._size, len( data ) ) )
            
            return
        
        raise ValueError( 'unsupported data type {0}'.format( type( data ) ) )

    def __str__(self):
        s = ''
        x = bytearray( struct.pack( '<HHBBxx', self._size, self._operation_id, self._type, self._result ) )
        for xx in x:
            s += "{0:0{1}x}".format( xx, 2 )
            s += ' '
        if self._payload is not None:
            for x in bytearray( self._payload ):
                s += "{0:0{1}x}".format( int( x ), 2 )
                s += ' '
        s = s.strip()
        
        return s
                
    def size(self):
        return self._size
    
    def operation_id(self, operation_id = None):
        if operation_id is None:
            return self._operation_id
        self._operation_id = operation_id
    
    def type(self):
        return self._type

    def result(self):
        return self._result 

    def payload(self, data = None):
        if data is None:
            return self._payload
        self._payload = data
        self._size = 8 + len( data )
    
    def isResponse(self):
        return True if ( GB_OP_RESPONSE & self._type ) else False
    
    def pack(self):
        hdr = str( struct.pack( '<HHBBxx', self._size, self._operation_id, self._type, self._result ) )
        pl = str( self._payload )
        msg = hdr + pl
        return buffer( msg )
    
    def response(self, result, payload = None ):
        
        if self.isResponse():
            raise ValueError( "cannot have a response to a response" )
        
        x = self
        x._type |= GB_OP_RESPONSE
        x._result = result
        if payload is None:
            x._payload = None
        else:
            x._payload = payload
            x._size = 8 + len( payload )

        return x
