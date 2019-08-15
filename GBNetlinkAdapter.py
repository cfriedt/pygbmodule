import select
import socket
import struct
import threading
from gnlpy import netlink

import GBOperationMessage

GB_NL_NAME = 'GREYBUS'

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

###
# Alternative 1: we use a callback and expose a sync
# write method to communicate between the SVC and the AP
#
# This makes the AP communication the "odd man out" in that
# GBSVCHandler would not be able to inherit from GBHandler
#
#
#self._netlink_message_callback( cport, msg )

##
# Alternative 2: we use a socketpair to communicate between
# the GBSVCHandler and the GBNetlinkAdapter.
# 
# This allows GBSVCHandler to inherit from GBHandler.
# However, it means we must bury the destination cport
# for a particular message inside of the GG header (in
# the pad field). The only concern there is that if 
# we need to pass more information than just the cport,
# then there would not be enough pad space.

class GBNetlinkAdapter(threading.Thread):

    #def __init__(self, netlink_message_callback):
    def __init__(self):

        threading.Thread.__init__(self)

        self.setupNetlinkSocket()
        self._cancellation_sock = socket.socketpair()
        #Alt1
        #self._netlink_message_callback = netlink_message_callback
        
        #Alt2
        self._greybus_sock = socket.socketpair()

        self._should_exit = False
        
        self._name = 'Netlink'

    def setupNetlinkSocket(self):

        self._netlink_sock_object = netlink.NetlinkSocket()
        family_id = self._netlink_sock_object.resolve_family( GB_NL_NAME )
        #print( '{} family resolves to id {}'.format( GB_NL_NAME, family_id ) )
        self._netlink_sock = self._netlink_sock_object.sock
        #print( 'netlink socket fd is {}'.format( self._netlink_sock.fileno() ) )

        self.resetGreybusHostDevice()

    def stop(self):
        self._should_exit = True
        self._cancellation_sock[ 1 ].send( 'q' )

    #Alt1
    def write(self, cport, msg):
        data = str( msg.pack() )

        message = GBNetlinkMessage(
            'GB_NL_C_MSG',
            flags=netlink.MessageFlags.REQUEST,
            attr_list=GBNetlinkCmdAttrList(GB_NL_A_DATA=data, GB_NL_A_CPORT=cport)
        )

        self._netlink_sock_object._send( message )
        print('Sent netlink message to cport {}: {}'.format(cport, msg))

    def resetGreybusHostDevice(self):
        # ACK should be corrected to NOACK, same with ACK_REQUEST
        message = GBNetlinkMessage(
            'GB_NL_C_HD_RESET',
            flags=netlink.MessageFlags.REQUEST
        )

        self._netlink_sock_object._send( message )

    def getSocketsWithData(self):

        sockets_with_data = []

        fd_to_socket = {
            self._cancellation_sock[ 0 ].fileno(): self._cancellation_sock[ 0 ],
            self._netlink_sock.fileno(): self._netlink_sock,
            self._greybus_sock[ 0 ].fileno(): self._greybus_sock[ 0 ],
        }

        READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
        poller = select.poll()
        poller.register( self._cancellation_sock[ 0 ], READ_ONLY )
        poller.register( self._netlink_sock, READ_ONLY )
        #Alt2
        poller.register( self._greybus_sock[ 0 ], READ_ONLY)

        events = poller.poll( -1 )

        for fd, flag in events:

            s = fd_to_socket[ fd ]

            if flag & (select.POLLHUP | select.POLLERR):
                msg = '{}: encountered an error on fd {}'.format( self._name, fd )
                print( msg )
                raise IOError( msg )

            if s is self._cancellation_sock[ 0 ]:
                msg = '{}: received data on cancellation fd {}'.format( self._name, fd )
                self._should_exit = True
                raise IOError( msg )

            if s is self._netlink_sock:
                #print('{}: netlink socket has data'.format(self._name))
                sockets_with_data.append( self._netlink_sock )
                continue

            if s is self._greybus_sock[ 0 ]:
                #print('{}: greybus socket has data'.format(self._name))
                sockets_with_data.append( self._greybus_sock[ 0 ] )
                continue


        return sockets_with_data

    def readBytes(self, sock, n):

        buf = bytearray(n)
        view = memoryview(buf)
        sz = 0
        
        while sz < n:
                
            sockets_with_data = []
            
            while sock not in sockets_with_data:
                sockets_with_data = self.getSocketsWithData()
                
                k = sock.recv_into(view[sz:],n-sz)
                sz += k
                break

        return buffer( buf )

    def run(self):
        
        print( '{} thread started..'.format( self._name ) )
        
        while not self._should_exit:

            try:

                sockets_with_data = self.getSocketsWithData()

                if self._netlink_sock in sockets_with_data:

                    #print('{}: reading from netlink socket..'.format(self._name))

                    nl_resp = self._netlink_sock_object._recv()[ 0 ]
                    attrs = nl_resp.get_attr_list()
                    cport = attrs.get('GB_NL_A_CPORT')
                    data = attrs.get('GB_NL_A_DATA')
                    msg = GBOperationMessage.GBOperationMessage( data )

                    ###
                    # Alternative 1: we use a callback and expose a sync
                    # write method to communicate between the SVC and the AP
                    #
                    # This makes the AP communication the "odd man out" in that
                    # GBSVCHandler would not be able to inherit from GBHandler
                    #
                    #
                    #self._netlink_message_callback( cport, msg )

                    ##
                    # Alternative 2: we use a socketpair to communicate between
                    # the GBSVCHandler and the GBNetlinkAdapter.
                    # 
                    # This allows GBSVCHandler to inherit from GBHandler.
                    # However, it means we must bury the destination cport
                    # for a particular message inside of the GG header (in
                    # the pad field). The only concern there is that if 
                    # we need to pass more information than just the cport,
                    # then there would not be enough pad space.

                    print('{}: received netlink message for cport {}: {}'.format(self._name, cport, msg))

                    msg.pad( struct.pack('<H', cport) )
                    
                    #print('{}: buried cport {} in padding: {}'.format(self._name, cport, msg))
                    
                    self._greybus_sock[ 0 ].sendall( msg.pack() )
                    print('{}: sent to fd {}: {}'.format(self._name, self._greybus_sock[ 0 ].fileno(), msg))
                    continue
                    
                if self._greybus_sock[ 0 ] in sockets_with_data:
                    
                    # any messages coming back this way are destined for
                    # the AP and should be using control port 0 already
                    # so we shouldn't even need to specify that here... right?
                    
                    #print('{}: reading header..'.format(self._name))
                    hdr = self.readBytes( self._greybus_sock[ 0 ], 8 )
                    msg = GBOperationMessage.GBOperationMessage( hdr )
                    
                    payload_size = msg.size() - 8
                    
                    if payload_size > 0:
                        #print('{}: reading {} bytes of payload..'.format(self._name, payload_size))
                        payload = self.readBytes( self._greybus_sock[ 0 ], payload_size )
                        msg.payload( payload )
                    
                    self.write( GBOperationMessage.GB_CONTROL_CPORT_ID, msg )
                    continue

            except Exception as e:
                print('{}: Exception: {}'.format(self._name, e))
                #if self._should_exit:
                #    break;
                break
        
        print( '{}: exiting..'.format( self._name ) )    
    
    def getGreybusSocket(self):
        return self._greybus_sock[ 1 ]
