#!/usr/bin/env python2

import socket
import struct
import time
import threading
from gnlpy import netlink

GB_NL_NAME = 'GREYBUS'
GB_NL_PID = 1        

GBNetlinkCmdAttrList = netlink.create_attr_list_type(
    'GBNetlinkCmdAttrList',
    ('GB_NL_A_DATA', netlink.BinaryType),
    ('GB_NL_A_CPORT', netlink.U16Type)
)

GBNetlinkMessage = netlink.create_genl_message_type(
    'GBNetlinkMessage', GB_NL_NAME,
    ('GB_NL_C_MSG', GBNetlinkCmdAttrList),
    ('GB_NL_C_HD_RESET', GBNetlinkCmdAttrList),
    required_modules=[],
)

class GBNetlinkAdapter(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.setupNetlinkSocket()
        self._greybus_sock = socket.socketpair()
        self._cancellation_sock = socket.socketpair()
        
        self._should_exit = False
    
    def setupNetlinkSocket(self):
        
        self._netlink_sock_object = netlink.NetlinkSocket()
        family_id = self._netlink_sock_object.resolve_family( GB_NL_NAME )
        print( '{} family resolves to id {}'.format( GB_NL_NAME, family_id ) )
        self._netlink_sock_object.port_id = GB_NL_PID
        print( 'set netlink port id to {}'.format( GB_NL_PID ) )
        self._netlink_sock = self._netlink_sock_object.sock
        print( 'netlink socket fd is {}'.format( self._netlink_sock.fileno() ) )
        
        # ACK should be corrected to NOACK, same with ACK_REQUEST
        message = GBNetlinkMessage('GB_NL_C_HD_RESET', flags=netlink.MessageFlags.ACK_REQUEST)
        
        self._netlink_sock_object._send( message )

    def stop(self):
        self._should_exit = True
        self._cancellation_sock[ 0 ].send( 'q' )
    
    def getGreybusSocket(self):
        return self._greybus_sock[ 1 ]
    
    def run(self):
        while not self._should_exit:
            time.sleep( 1 )

if __name__ == '__main__':
    
    blah = GBNetlinkAdapter()
    blah.start()
    time.sleep( 5 )
    blah.stop()
    blah.join()
