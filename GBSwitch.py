import threading

class GBSwitch(threading.Thread):
    
    def __init__(self):
        # cport id to GBCPort object
        self._cports = {}
        # interface id to GBInterface object
        self._interfaces = {}
        # 
        self._routes = {}
        self._connections = {}
        self._cport_to_socket = {}
        self._socket_to_cport = {}
        pass

    