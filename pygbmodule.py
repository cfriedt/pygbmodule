#!/usr/bin/env python2

# Test program for using Avahi in Python. Publishes a dummy service.

from __future__ import print_function


import socket
import avahi
import dbus
import signal
import time

from GBControlHandler import GBControlHandler
from GBGPIOHandler import GBGPIOHandler

SHOULD_EXIT = False

def sighandler(signum, frame):  # @UnusedVariable
    global SHOULD_EXIT
    print( 'caught signal {}'.format( signum ) )
    #print( 'SHOULD_EXIT set to True' )
    SHOULD_EXIT = True

def main():
    global SHOULD_EXIT

    with open('manifest.mnfb', mode='rb') as file:
        manifest = file.read()
    
    # Avahi Service details
    avahi_name = "Greybus IoT Device"
    avahi_port = 18242
    avahi_service_type = "_greybus._tcp"
    avahi_domain = ""
    avahi_host = ""
    avahi_text = ["hello=world"]
    
    control_server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    control_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print( 'created control server socket' )
    control_server_addr = ('',avahi_port)
    control_server_socket.bind( control_server_addr )
    print( 'bound control server to {0}'.format( control_server_addr ) )
    control_server_socket.listen(1)
    print( 'control server listening for incoming connections..' )
    control_hdlr = GBControlHandler( control_server_socket, manifest )
    control_hdlr.start()

    gpio_server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    gpio_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print( 'created gpio server socket' )
    gpio_server_addr = ('',avahi_port+1)
    gpio_server_socket.bind( gpio_server_addr )
    print( 'bound gpio server to {0}'.format( gpio_server_addr ) )
    gpio_server_socket.listen(1)
    print( 'gpio server listening for incoming connections..' )
    gpio_hdlr = GBGPIOHandler( gpio_server_socket )
    gpio_hdlr.start()

    iface = avahi.IF_UNSPEC
    bus = dbus.SystemBus()
    server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)
    g = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.EntryGroupNew()), avahi.DBUS_INTERFACE_ENTRY_GROUP)
    g.AddService(iface, avahi.PROTO_UNSPEC, dbus.UInt32(0), avahi_name, avahi_service_type, avahi_domain, avahi_host, dbus.UInt16(avahi_port), avahi.string_array_to_txt_array(avahi_text))
    g.Commit()

    signal.signal( signal.SIGINT, sighandler )
    signal.signal( signal.SIGTERM, sighandler )
    signal.signal( signal.SIGHUP, sighandler )
    print('installed signal handler..')

    while not SHOULD_EXIT:
        #print( 'SHOULD_EXIT is not set..' )
        time.sleep( 1 )
        
    control_hdlr.stop()
    control_hdlr.join()
    print( 'control handler thread joined' )

    gpio_hdlr.stop()
    gpio_hdlr.join()
    print( 'gpio handler thread joined' )
    
    g.Reset()
    print( 'reset avahi' )

if __name__ == "__main__":
    main()
