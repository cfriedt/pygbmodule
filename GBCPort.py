class GBCPort(object):
    
    def __init__(self, cport_id, sock):
        self._cport_id = cport_id
        self._sock = sock
    
    def cport_id(self):
        return self._cport_id
    