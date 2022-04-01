#   --- Turms ---
#   Handler for making requests from user to server
#   and delegating answers
#
#   Sipi Ylä-Nojonen, 2022

from ipaddress import ip_address
import logging as log

import requests as req

class ConnectionHandler():
    def __init__(self):
        pass

    def connect_to_server(self, ipaddr, port):
        """
        Attempt to create a connection to specified server.

        :param ipaddr:  Address of the server. Should be valid ip-address.
        :param port:    Port to attempt to send the request.
        :return:
        """

        try:
            ip = ip_address(ipaddr) # Raises ValueError if not valid ip-address
        except ValueError:
            log.warning("Given address is not valid ip-address.")

    def make_request(self, meth="HEAD", path="/"):
        """
        Make request to the server

        :param meth: Request method, compliant with HTTP/1.1
        :param path: url path to fetch.
        :return:
        """

        request = req.Request(method=meth, url=path)
        request.prepare()
        return
