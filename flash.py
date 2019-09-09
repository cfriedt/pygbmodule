#!/usr/bin/env python2.7

import os
import serial
import struct
import sys
import time

import GBOperationMessage

GB_TYPE_MANIFEST_SET = 0x42

operation_id = 1

def usage(progname):
    print('usage: python3 {} </dev/ttyACM0> <manifest.mnfb>'.format(progname))

def sendMessage(ser, msg):
    global operation_id
    msg.operation_id( operation_id )
    operation_id += 1
    ser.write(msg.pack())

def getMessage(ser, expected_msg_type):

    data = ''
    offset = 0
    remaining = 8
    recvd = 0

    while remaining > 0:
        newdata = ser.read(remaining)
        recvd = len(newdata)
        if 0 == recvd:
            time.sleep(0.1)
            continue
        remaining -= recvd
        offset += recvd
        data += newdata


    msg = GBOperationMessage.GBOperationMessage(data)

    payload_size = msg.size() - 8
    if payload_size > 0:
        payload = ser.read(payload_size)
        msg.payload(payload)

    if expected_msg_type != msg.type():
        raise ValueError('unexpected message type {}'.format(msg.type()))

    return msg

def main(argv):

    if len(argv) != 3:
        usage(os.path.basename(argv[0]))
	return 0

    #with serial.Serial(argv[1], 115200, timeout=0.1) as ser:
    with serial.Serial(argv[1], 115200, timeout=1) as ser:
        print('using ser {}'.format(ser))

        with open(argv[2], 'r') as mnfbFile:

            print('using mnfbFile {}'.format(mnfbFile))

            mnfb = mnfbFile.read()

            payload_size = len(mnfb)
            msg_size = 8 + payload_size

            print('sending manifest..')

            msg = GBOperationMessage.GBOperationMessage(struct.pack('<HHBBxx', msg_size, 1, GB_TYPE_MANIFEST_SET, 0))
            msg.payload(mnfb)

            sendMessage(ser,msg)

            print('awaiting response')

            msg = getMessage(ser, GB_TYPE_MANIFEST_SET | GBOperationMessage.GB_OP_RESPONSE)

            print('received response')
            
            r = msg.result()
            
            if GBOperationMessage.GB_OP_SUCCESS != r:
                print('flashing failed {}'.format(r))
            else:
                print('OK')

            return r

if __name__ == '__main__':
    sys.exit(main(sys.argv))
