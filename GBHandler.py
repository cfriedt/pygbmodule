import select
import socket
import threading

import GBOperationMessage
from __builtin__ import True
from GBOperationMessage import GB_OP_RESPONSE, GB_OP_PROTOCOL_BAD

class GBHandler(threading.Thread):
    
    def __init__(self, sock, handlers = {}):
        
        threading.Thread.__init__(self)
        
        self._server_sock = sock
        self._handlers = handlers
        self._should_exit = False
        self._name = '?????'
        # only used for messages that originate from this object!
        self._operation_id = 1
        
        self._cancellation = socket.socketpair()
    
    def readBytes(self, nbytes):
        fd_to_socket = {
            self._client_sock.fileno(): self._client_sock,
            self._cancellation[ 0 ].fileno(): self._cancellation[ 0 ],
        }

        READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
        poller = select.poll()
        poller.register( self._client_sock, READ_ONLY )
        poller.register( self._cancellation[ 0 ], READ_ONLY )
        
        events = poller.poll( -1 )
        for fd, flag in events:

            s = fd_to_socket[ fd ]
            if s is self._cancellation[ 0 ]:
                msg = '{}: received data on cancellation fd {}'.format( self._name, fd )
                print( msg )
                self._should_exit = True
                raise IOError( msg )
            
            if flag & (select.POLLHUP | select.POLLERR):
                msg = '{}: encountered an error on fd {}'.format( self._name, fd )
                print( msg )
                raise IOError( msg )

            hdr = self._client_sock.recv( nbytes )
            return hdr

    def accept(self):
        fd_to_socket = {
            self._server_sock.fileno(): self._server_sock,
            self._cancellation[ 0 ].fileno(): self._cancellation[ 0 ],
        }

        READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
        poller = select.poll()
        poller.register( self._server_sock, READ_ONLY )
        poller.register( self._cancellation[ 0 ], READ_ONLY )
        
        events = poller.poll( -1 )
        for fd, flag in events:

            s = fd_to_socket[ fd ]
            if s is self._cancellation[ 0 ]:
                msg = '{}: received data on cancellation fd {}'.format( self._name, fd )
                print( msg )
                self._should_exit = True
                raise IOError( msg )
            
            if flag & (select.POLLHUP | select.POLLERR):
                msg = '{}: encountered an error on fd {}'.format( self._name, fd )
                print( msg )
                raise IOError( msg )

            return self._server_sock.accept()
    
    
    def run(self):
        
        print( '{} thread started..'.format( self._name ) )
        
        while not self._should_exit:

            try:
                self._client_sock, self._client_addr = self.accept()
            except:
                break;            

            while True:

                try:
                    hdr = self.readBytes( 8 )
                    msg = GBOperationMessage.GBOperationMessage( hdr )
                    payload_len = msg.size() - 8

                    if payload_len < 0:
                        raise ValueError( 'impossible message size of {0}'.format( msg.size() ) )
    
                    if payload_len > 0:                        
                        payload = buffer( self.readBytes( payload_len ) )
                        msg.payload( payload )
                    
                    hdlr = self._handlers[ msg.type() ]
                    if hdlr is None:
                        if not msg.isResponse():
                            resp = msg.response(GB_OP_PROTOCOL_BAD)
                        print( 'unhandled message type {0}'.format( msg.type() ) )
                        continue
                    
                    print( '{}: received: {} {}: {}'.format(
                        self._name,
                        'resp' if msg.isResponse() else 'req ',
                        self.identify( msg.type() & ~GB_OP_RESPONSE ),
                        msg
                    ))

                    if msg.isResponse():
                        resp = msg
                        hdlr( self, resp )
                    else:
                        req = msg
                        resp = hdlr( self, req )
                        self.send( resp )
                except Exception as e:
                    print('Encountered exception {}'.format(e))
                    break
            
            try:
                self._client_sock.close()
            except:
                pass

        print( '{}: exiting..'.format( self._name ) )
    
    def send(self, msg):

        self._client_sock.send( msg.pack() )
        
        print( '{}: sent    : {} {}: {}'.format(
            self._name,
            'resp' if msg.isResponse() else 'req ',
            self.identify( msg.type() & ~GB_OP_RESPONSE ),
            msg
        ))
    
    def stop(self):
        self._should_exit = True
        self._cancellation[ 1 ].send( buffer( 'q' ) )

    def identify(self, message_type):  # @UnusedVariable
        return '????'