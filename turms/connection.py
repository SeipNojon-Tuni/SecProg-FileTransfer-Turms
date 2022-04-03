#   --- Turms ---
#   Virtual representation of connection to
#   a server. Since
#
#   Sipi Ylä-Nojonen, 2022

import requests as req

class Connection():

    __url = None

    def __init__(self, ipaddr, port):
        __url ="https://%s:%s" % (ipaddr, port)  # build url for requests, 'http://ip:port'

    def path(self, route):
        return "%s/%s" % (self.__url, route)

    def get(self, route):
        url = self.path(route)
        return req.get(url)

    def head(self, route):
        url = self.path(route)
        return req.head(url)