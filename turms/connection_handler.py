#   --- Turms ---
#   Handler for making requests from client to server
#   and delegating answers
#
#   Sipi Ylä-Nojonen, 2022
import sys
from ipaddress import ip_address
import logger

import tornado.simple_httpclient
import tornado.httpclient
import asyncio


class ConnectionHandler:
    __session = None
    __server_url = None

    def __init__(self):
        pass

    async def connect_to_server(self, ipaddr, port, controller):
        """
        Attempt to create a connection to specified server.

        :param ipaddr:  Address of the server. Should be valid ip-address.
        :param port:    Port to attempt to send the request.
        :return:        Whether connection was successful ( or already connected)
        """

        try:
            # Allow connection only when no former connection is active.
            if self.__session or self.__server_url:
                logger.info("Already connected to a server. Please terminate connection first.")
                return

            ip = ip_address(ipaddr)                     # Raises ValueError if not valid IPv4 or IPv6 address
            portint = int(port)

            url = "http://%s:%s" % (ipaddr, portint)

            self.__server_url = url
            self.__session = tornado.httpclient.AsyncHTTPClient()

            logger.info("Connecting to " + url)

            response = self.make_request("/")  # Default path "/"

            logger.info(str(response.code))
            logger.info(response.body)

            return
        except tornado.simple_httpclient.HTTPTimeoutError:
            logger.error("Connection timed out.")
            self.disconnect_from_server(controller)
            return

        except ValueError:
            logger.warning("Invalid ip-address or port given.")
            self.disconnect_from_server(controller)
            return

        # Could not establish connection
        except ConnectionError:
            logger.warning("Failed to establish connection.")
            self.disconnect_from_server(controller)
            return

    def disconnect_from_server(self, controller):
        """ Attempt to disconnect from server if connection is active """

        if self.__session:
            self.__session.close()
            self.__session = None

        self.__server_url = None
        controller.state_to_disconnect()

        return

    async def make_request(self, path="/"):
        """
        Make request to the server

        :param meth: Request method, compliant with HTTP/1.1
        :param path: url path to fetch.
        :return:     Response got from the server
        """

        if self.__session and self.__server_url:
            url = "%s:%s" % (self.__server_url, path)
            response = await self.__session.fetch(url)
            return response
