import select
import socket
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

class GBNetlinkAdapter(threading.Thread):

    def __init__(self, netlink_message_callback):

        threading.Thread.__init__(self)

        self.setupNetlinkSocket()
        self._cancellation_sock = socket.socketpair()
        self._netlink_message_callback = netlink_message_callback

        self._should_exit = False

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

    def write(self, cport, msg):
        data = str( msg.pack() )

        message = GBNetlinkMessage(
            'GB_NL_C_MSG',
            flags=netlink.MessageFlags.REQUEST,
            attr_list=GBNetlinkCmdAttrList(GB_NL_A_DATA=data, GB_NL_A_CPORT=cport)
        )

        self._netlink_sock_object._send( message )
        #print('Sent netlink message to cport {}: {}'.format(cport, msg))

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
        }

        READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
        poller = select.poll()
        poller.register( self._cancellation_sock[ 0 ], READ_ONLY )
        poller.register( self._netlink_sock, READ_ONLY )

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

                sockets_with_data.append( self._netlink_sock )
                continue

        return sockets_with_data

    def readBytes(self, sock, nbytes):

        sockets_with_data = []

        while sock not in sockets_with_data:
            sockets_with_data = self.getSocketsWithData()

        data = sock.recv( nbytes )

        return data

    def run(self):
        while not self._should_exit:

            try:

                sockets_with_data = self.getSocketsWithData()

                if self._netlink_sock in sockets_with_data:

                    nl_resp = self._netlink_sock_object._recv()[ 0 ]
                    attrs = nl_resp.get_attr_list()
                    cport = attrs.get('GB_NL_A_CPORT')
                    data = attrs.get('GB_NL_A_DATA')
                    msg = GBOperationMessage.GBOperationMessage( data )

                    #print('Received netlink message for cport {}: {}'.format(cport, msg))

                    self._netlink_message_callback( cport, msg )

            except:
                if self._should_exit:
                    break;
