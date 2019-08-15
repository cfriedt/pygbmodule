#!/usr/bin/env python2.7

# Test program for using Avahi in Python. Publishes a dummy service.

from __future__ import print_function


import socket
import avahi
import dbus
import signal
import time

from GBControlHandler import GBControlHandler
from GBGPIOHandler import GBGPIOHandler
from GBSVCHandler import GBSVCHandler
import GBNetlinkAdapter

# Avahi Service details
avahi_name = "Greybus IoT Device"
avahi_port = 18242
avahi_service_type = "_greybus._tcp"
avahi_domain = ""
avahi_host = ""
avahi_text = ["hello=world"]

manifest = []

def setupControlHandler():
    
    global avahi_port
    global manifest
    
    control_server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    control_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print( 'created control server socket' )
    control_server_addr = ('',avahi_port)
    control_server_socket.bind( control_server_addr )
    print( 'bound control server to {0}'.format( control_server_addr ) )
    control_server_socket.listen(1)
    print( 'control server listening for incoming connections..' )
    control_hdlr = GBControlHandler( control_server_socket, manifest )
    return control_hdlr

def setupGpioHandler( ngpio ):
    gpio_server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    gpio_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print( 'created gpio server socket' )
    gpio_server_addr = ('',avahi_port+1)
    gpio_server_socket.bind( gpio_server_addr )
    print( 'bound gpio server to {0}'.format( gpio_server_addr ) )
    gpio_server_socket.listen(1)
    print( 'gpio server listening for incoming connections..' )
    gpio_hdlr = GBGPIOHandler( gpio_server_socket, ngpio )
    return gpio_hdlr

def setupAvahiServiceAdvertisement():
    iface = avahi.IF_UNSPEC
    bus = dbus.SystemBus()
    server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)
    avahi_dbus_interface = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.EntryGroupNew()), avahi.DBUS_INTERFACE_ENTRY_GROUP)
    avahi_dbus_interface.AddService(iface, avahi.PROTO_UNSPEC, dbus.UInt32(0), avahi_name, avahi_service_type, avahi_domain, avahi_host, dbus.UInt16(avahi_port), avahi.string_array_to_txt_array(avahi_text))
    avahi_dbus_interface.Commit()
    return avahi_dbus_interface

should_exit = False

def sighandler(signum, frame):  # @UnusedVariable
    global should_exit

    print( 'caught signal {}'.format( signum ) )
    #print( 'should_exit set to True' )
    should_exit = True

def setupSignalHandlers():
    signal.signal( signal.SIGINT, sighandler )
    signal.signal( signal.SIGTERM, sighandler )
    signal.signal( signal.SIGHUP, sighandler )
    print('installed signal handler..')

def main():
    global should_exit
    global manifest

    with open('manifest.mnfb', mode='rb') as f:
        manifest = f.read()

    control_hdlr = setupControlHandler()
    control_hdlr.start()
    
    ngpio = 1
    gpio_hdlr = setupGpioHandler( ngpio )
    gpio_hdlr.start()

    avahi_dbus_interface = setupAvahiServiceAdvertisement()

    setupSignalHandlers()

#    gb_nl_adapter = GBNetlinkAdapter.GBNetlinkAdapter()
#    gb_nl_adapter.start()
#
#    svc_handler = GBSVCHandler( gb_nl_adapter.getGreybusSocket() )
#    svc_handler.start()
#    svc_handler.connectToAP()

    while not should_exit:
        #print( 'should_exit is not set..' )
        time.sleep( 1 )

#    svc_handler.stop()
#    svc_handler.join()
#
#    gb_nl_adapter.stop()
#    gb_nl_adapter.join()

    control_hdlr.stop()
    control_hdlr.join()

    gpio_hdlr.stop()
    gpio_hdlr.join()
    
    avahi_dbus_interface.Reset()

if __name__ == "__main__":
    main()
