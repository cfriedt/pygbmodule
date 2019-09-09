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

    data = []

    while True:
        data = ser.read(8)
        if 0 == len(data):
            time.sleep(0.1)

    msg = GBOperationMessage.GBOperationMessage(ser.read(8))

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

    with serial.Serial(argv[1], 115200, timeout=0.1) as ser:
        print('using ser {}'.format(ser))

        with open(argv[2], 'r') as mnfbFile:

            print('using mnfbFile {}'.format(mnfbFile))

            mnfb = mnfbFile.read()

            payload_size = len(mnfb)
            msg_size = 8 + payload_size

            msg = GBOperationMessage.GBOperationMessage(struct.pack('<HHBBxx', msg_size, 1, GB_TYPE_MANIFEST_SET, 0))
            msg.payload(mnfb)

            sendMessage(ser,msg)

            msg = getMessage(ser, GB_TYPE_MANIFEST_SET | GBOperationMessage.GB_OP_RESPONSE)

            return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
