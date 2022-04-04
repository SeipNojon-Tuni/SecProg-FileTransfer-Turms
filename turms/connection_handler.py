#   --- Turms ---
#   Handler for making requests from user to server
#   and delegating answers
#
#   Sipi Ylä-Nojonen, 2022

from ipaddress import ip_address
import logger

import requests
import requests.exceptions as exc

class ConnectionHandler():
    __session = None
    __server_url = None

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
            # Allow connection only when no former connection is active.
            if self.__session or self.__server_url:
                log.info("Already connected to a server. Please terminate connection first.")
                return

            ip = ip_address(ipaddr)                     # Raises ValueError if not valid IPv4 or IPv6 address
            portint = int(port)

            url = "https://%s:%s" % (ipaddr, port)      # build url for requests, http://ip:port instead of DNS url.

            self.__server_url = url
            self.__session = requests.Session()

        except ValueError:
            logger.warning("Invalid ip-address or port given.")
            return

        # Could not establish connection
        except exc.ConnectionError:
            logger.warning("Failed to establish connection.")
            pass

    def disconnect_from_server(self):
        """ Attempt to disconnect from server if connection is active """

        if self.active_connection():
            self.__session.close()
            self.__session = None
            self.__server_url = None

    def make_request(self, meth, path):
        """
        Make request to the server

        :param meth: Request method, compliant with HTTP/1.1
        :param path: url path to fetch.
        :return:
        """

        url = "%s:%s" % (self.__server_url, path)

        if self.active_connection():
            response = self.__session.request(method=meth, url=url, verify=False)   # Ignore TLS certificate
        return                                                                      # verification

    def active_connection(self):
        """ Return whether currently connected to server """

        # Return True if connection exists
        return lambda : True if self.__session is not None else False