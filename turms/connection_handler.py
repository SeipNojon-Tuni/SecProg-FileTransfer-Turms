#   --- Turms ---
#   Handler for making requests from user to server
#   and delegating answers
#
#   Sipi Ylä-Nojonen, 2022

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

    async def connect_to_server(self, ipaddr, port):
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
                return True

            ip = ip_address(ipaddr)                     # Raises ValueError if not valid IPv4 or IPv6 address
            portint = int(port)

            url = "https://%s:%s" % (ipaddr, port)      # build url for requests, http://ip:port instead of DNS url.

            self.__server_url = url
            self.__session = tornado.httpclient.AsyncHTTPClient()

            response = await self.__session.fetch(url+"/")
            logger.info(response.body)

            return True
        except tornado.simple_httpclient.HTTPTimeoutError:
            logger.error("Connection timed out.")
            return False

        except ValueError:
            logger.warning("Invalid ip-address or port given.")
            return False

        # Could not establish connection
        except ConnectionError:
            logger.warning("Failed to establish connection.")
            return False

    def disconnect_from_server(self):
        """ Attempt to disconnect from server if connection is active """

        if self.__session:
            self.__session.close()
            self.__session = None
            self.__server_url = None

        return True

    def make_request(self, meth, path):
        """
        Make request to the server

        :param meth: Request method, compliant with HTTP/1.1
        :param path: url path to fetch.
        :return:
        """

        url = "%s:%s" % (self.__server_url, path)

        if self.__session:
            response = self.__session.request(method=meth, url=url, verify=False)   # Ignore TLS certificate
        return                                                                      # verification
