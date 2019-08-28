import os
import select
import socket
import threading

from Crypto import Random
from Crypto.Cipher import AES

import GBOperationMessage
import GBPKAuthHandler
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
        
        self._client_sock = -1
        self._client_sock_is_static = False
    
    def getSocketsWithData(self):
        
        sockets_with_data = []
        
        fd_to_socket = {
            self._cancellation[ 0 ].fileno(): self._cancellation[ 0 ],
        }
        
        if self._client_sock != -1:
            fd_to_socket[ self._client_sock.fileno()] = self._client_sock
        
        if self._server_sock != -1:
            fd_to_socket[ self._server_sock.fileno()] = self._server_sock
    
        READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
        poller = select.poll()
        if self._server_sock != -1:            
            poller.register( self._server_sock, READ_ONLY )
        if self._client_sock != -1:    
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
            
            if s is self._client_sock:
                sockets_with_data.append( s )

            if s is self._server_sock:
                sockets_with_data.append( s )
        
        return sockets_with_data

    def readBytes(self, n):
        
        buf = bytearray(n)
        view = memoryview(buf)
        sz = 0
        
        sock = self._client_sock
        
        while sz < n:
                
            sockets_with_data = []
            while sock not in sockets_with_data:
                sockets_with_data = self.getSocketsWithData()

            k = sock.recv_into(view[sz:],n-sz)
            sz += k
            break

        return buffer( buf )

    def accept(self):
        
        sockets_with_data = []
        while self._server_sock not in sockets_with_data:
            sockets_with_data = self.getSocketsWithData()

        return self._server_sock.accept()
    
    def run(self):
        
        print( '{} thread started..'.format( self._name ) )
        
        while not self._should_exit:

            if not self._client_sock_is_static:
                try:
                    self._client_sock, self._client_addr = self.accept()

                    id_rsa_path = os.environ['HOME'] + '/.ssh/id_rsa'
                    authorized_keys_path = os.environ['HOME'] + '/Desktop/authorized_keys'
                    pkauth = GBPKAuthHandler.GBPKAuthHandler(self._client_sock, id_rsa_path, authorized_keys_path)

                    self._session_key = pkauth.auth()

                except Exception as e:
                    print('{}: caught exception: {}'.format(self._name, e))
                    self._client_sock = None
                    self._client_addr = None
                    break

            while True:

                try:
                    msg = self.getMessage()

                    hdlr = self._handlers[ msg.type() ]
                    if hdlr is None:
                        self.missingHandler( msg )
                        continue
                    
                    if msg.isResponse():
                        resp = msg
                        hdlr( self, resp )
                    else:
                        req = msg
                        resp = hdlr( self, req )
                        self.send( resp )
                except Exception as e:
                    print('{}: Encountered exception {}'.format(self._name, e))
                    self._should_exit = True
                    break
            
            try:
                self._client_sock.close()
            except Exception as e:
                pass

        print( '{}: exiting..'.format( self._name ) )

    def send(self, msg):

        plaintext = str(msg.pack())

        ciphertext = self.encrypt( plaintext )

        self._client_sock.send( ciphertext )
        
        print( '{}: sent    : {} {}: {}'.format(
            self._name,
            'resp' if msg.isResponse() else 'req ',
            self.identify( msg.type() & ~GB_OP_RESPONSE ),
            msg
        ))
    
    def encrypt(self, plaintext):
        pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size) 
        plaintext = pad( plaintext )
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self._session_key, AES.MODE_CBC, iv )
        ciphertext = iv + cipher.encrypt(plaintext)
        return ciphertext
    
    def getMessage(self):

        iv = self.readBytes( AES.block_size )
        ciphertext = self.readBytes( AES.block_size )
        decipher = AES.new( self._session_key, AES.MODE_CBC, iv )
        plaintext = decipher.decrypt(ciphertext)
        
        hdr = plaintext[:8]
        msg = GBOperationMessage.GBOperationMessage( hdr )
        payload_len = msg.size() - 8
        
        nblocks = msg.size() // AES.block_size
        nblocks += 0 if (msg.size() % AES.block_size) == 0 else 1
        
        if nblocks > 1:
            ciphertext = self.readBytes( nblocks * AES.block_size )
            plaintext += decipher.decrypt( ciphertext )

        plaintext = plaintext[:msg.size()]

        if payload_len > 0:        
            payload = plaintext[8:msg.size()]
            msg.payload(payload)
        else:
            payload = None
        
        print( '{}: received: {} {}: {}'.format(
            self._name,
            'resp' if msg.isResponse() else 'req ',
            self.identify( msg.type() ),
            msg
        ))
        
        return msg
    
    def stop(self):
        self._should_exit = True
        self._cancellation[ 1 ].send( buffer( 'q' ) )

    def identify(self, message_type):  # @UnusedVariable
        return '????'
    
    # XXX: shouldn't need to do this. GBSwitch should take care of all routing
    def missingHandler(self, msg):
        print( '{}: unhandled message: {}'.format( self._name, msg ) )

        if not msg.isResponse():
            resp = msg.response(GB_OP_PROTOCOL_BAD)
            self.send( resp )
