import os
import random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import struct

from GBOperationMessage import (
    GB_OP_SUCCESS,
    GB_OP_RESPONSE,
    GB_VERSION_MAJOR,
    GB_VERSION_MINOR,
)

import GBOperationMessage
from pip.utils import outdated

GB_PKAUTH_TYPE_VERSION = 0x7b
GB_PKAUTH_TYPE_PUBKEY = 0x7c
GB_PKAUTH_TYPE_CHALLENGE = 0x7d
GB_PKAUTH_TYPE_CHALLENGE_RESP = 0x7e

GB_PKAUTH_VERSION_MAJOR = 0x00
GB_PKAUTH_VERSION_MINOR = 0x01

GB_PKAUTH_PUBKEY_RESULT_SUCCESS = 0x00
GB_PKAUTH_PUBKEY_RESULT_NOAUTH  = 0x01

class GBPKAuthHandler(object):
        
    def __init__(self, sock, id_rsa_path, authorized_keys_path):
        self._name = "PKAuth"
        self._client_sock = sock

        with open( id_rsa_path, 'rb' ) as f:
            self._id_rsa = RSA.importKey( f.read(), passphrase = None )

        with open(authorized_keys_path, mode='rb') as f:
            self._authorized_keys = f.read().strip()

        self._operation_id = 1
        
        self._cipher = PKCS1_OAEP.new( self._id_rsa )
    
    def getOperationId(self):
        oid = self._operation_id
        self._operation_id = self._operation_id + 1
        return oid
    
    def getPubKey(self):
        keytext = self._id_rsa.publickey().exportKey()
        # if dealing with a "BEGIN PUBLIC KEY" type public key
        # convert it to a "BEGIN RSA PUBLIC KEY" type.
        keytext = keytext.replace('BEGIN PUBLIC KEY', '')
        keytext = keytext.replace('END PUBLIC KEY', '')
        keytext = keytext.replace('-', '')
        keytext = keytext.replace('\n', '')
        keytext = keytext[32:]
        out = ''
        for i in range(0,len(keytext)):
            out = out + keytext[i]
            if 63 == (i % 64) and i != len(keytext) - 1:
                out = out + '\n'
        out = '-----BEGIN RSA PUBLIC KEY-----\n' + out
        out = out + '\n' + '-----END RSA PUBLIC KEY-----'
        return out
     
    def readBytes(self, n):
        
        buf = bytearray(n)
        view = memoryview(buf)
        sz = 0
        
        sock = self._client_sock
        
        while sz < n:
                
            k = sock.recv_into(view[sz:],n-sz)
            sz += k
            break

        return buffer( buf )

    def send(self, msg):

        self._client_sock.send( msg.pack() )
        
        print( '{}: sent    : {} {}: {}'.format(
            self._name,
            'resp' if msg.isResponse() else 'req ',
            self.identify( msg.type() & ~GB_OP_RESPONSE ),
            msg
        ))

    def getMessage(self, expected_type):

        hdr = self.readBytes( 8 )
        msg = GBOperationMessage.GBOperationMessage( hdr )
        payload_len = msg.size() - 8
        
        if payload_len > 0:
            payload = self.readBytes( payload_len )
            msg.payload(payload)
        
        print( '{}: received: {} {}: {}'.format(
            self._name,
            'resp' if msg.isResponse() else 'req ',
            self.identify( msg.type() ),
            msg
        ))
        
        if msg.type() != expected_type:
            self.send(msg.response(GBOperationMessage.GB_OP_INVALID))
            raise ValueError('{}: unexpected message type {}'.format(self._name, self.identify(msg.type())))
        
        return msg

    def identify(self, t):
        t &= ~GB_OP_RESPONSE
        if GB_PKAUTH_TYPE_VERSION == t:        return 'GB_PKAUTH_TYPE_VERSION       ' 
        if GB_PKAUTH_TYPE_PUBKEY == t:         return 'GB_PKAUTH_TYPE_PUBKEY        '
        if GB_PKAUTH_TYPE_CHALLENGE == t:      return 'GB_PKAUTH_TYPE_CHALLENGE     '
        if GB_PKAUTH_TYPE_CHALLENGE_RESP == t: return 'GB_PKAUTH_TYPE_CHALLENGE_RESP'
        return None

    def VERSION(self):
        req_payload = struct.pack( 'BB', GB_PKAUTH_VERSION_MAJOR, GB_PKAUTH_VERSION_MINOR )
        req = GBOperationMessage.GBOperationMessage((self.getOperationId(),GB_PKAUTH_TYPE_VERSION, req_payload))
        self.send(req)
        resp = self.getMessage( GB_PKAUTH_TYPE_VERSION | GB_OP_RESPONSE )
        (major,minor) = struct.unpack('BB', resp.payload())
        if not(GB_PKAUTH_VERSION_MAJOR == major and GB_PKAUTH_VERSION_MINOR == minor):
            raise ValueError('{}: incompatible protocol version: {}.{}'.format(self._name, major, minor))
 
    def PUBKEY(self):
        req_payload = buffer( self.getPubKey() )
        req = GBOperationMessage.GBOperationMessage((self.getOperationId(),GB_PKAUTH_TYPE_PUBKEY, req_payload))
        self.send(req)
        resp = self.getMessage(GB_PKAUTH_TYPE_PUBKEY | GB_OP_RESPONSE)
        if resp.size() != 9:
            raise ValueError('{}: PUBKEY response only has 9 bytes'.format(self._name))
        if resp.result() != GB_OP_SUCCESS:
            raise ValueError('{}: cannot authenticate with public key'.format(self._name))
 
    def handle_PUBKEY(self):
        msg = self.getMessage( GB_PKAUTH_TYPE_PUBKEY )
        pubkey = str(msg.payload()).strip()
        self._device_cipher = PKCS1_OAEP.new( RSA.importKey( pubkey, passphrase = None ) )
        result = GB_PKAUTH_PUBKEY_RESULT_NOAUTH
        if pubkey in self._authorized_keys:
            result = GB_PKAUTH_PUBKEY_RESULT_SUCCESS
        payload = struct.pack('B', result)
        self.send( msg.response( GB_OP_SUCCESS, payload ) )
 
    def CHALLENGE(self):
        clear_text_len = random.randint(200,300)
        clear_text = os.urandom( clear_text_len )
        cipher_text = self._device_cipher.encrypt( clear_text )
        payload = buffer( cipher_text )
        req = GBOperationMessage.GBOperationMessage((self.getOperationId(), GB_PKAUTH_TYPE_CHALLENGE, payload))
        self.send(req)
        resp = self.getMessage(GB_PKAUTH_TYPE_CHALLENGE | GB_OP_RESPONSE)
        if resp.status() != GB_OP_SUCCESS:
            raise ValueError( 'unexpected status {}'.format( resp.status() ) )

    def handle_CHALLENGE(self):
        msg = self.getMessage( GB_PKAUTH_TYPE_CHALLENGE )
        self.send(msg.response(GB_OP_SUCCESS))

    def handle_CHALLENGE_RESP( self, msg ):
        return msg.response( GB_OP_SUCCESS )
    
    def auth(self):
        self.VERSION()
        self.PUBKEY()
        self.handle_PUBKEY()
        self.CHALLENGE()
        self.handle_CHALLENGE_RESP()
        self.handle_CHALLENGE()
        self.CHALLENGE_RESP()

        