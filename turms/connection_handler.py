#   --- Turms ---
#   Handler for making requests from user to server
#   and delegating answers
#
#   Sipi Ylä-Nojonen, 2022

from ipaddress import ip_address
import logging as log

import requests.exceptions as exc
import connection as con

class ConnectionHandler():
    __connection = None

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
            ip = ip_address(ipaddr)                     # Raises ValueError if not valid ip-address
            portint = int(port)                         # Should be integer value

            url = "https://%s:%s" % (ipaddr, port)      # build url for requests, http://ip:port


            __connection = con.Connection(ipaddr, port) # Create connection object to represent the
                                                        # connection to server.

        except ValueError:
            self.__connection = None
            log.warning("Invalid ip-address or port given.")

        # Could not establish connection
        except exc.ConnectionError:
            pass


    def disconnect_from_server(self):
        """ Attempt to disconnect from server if connection is active """

        if self.active_connection():
            pass


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


    def active_connection(self):
        """ Return whether currently connected to server """

        # Return True if connection exists
        return lambda : True if self.__connection is not None else False