#   --- Turms ---
#   Handler for making requests from client to server
#   and delegating answers
#
#   Sipi Ylä-Nojonen, 2022
import socket
import sys
from ipaddress import ip_address

import logger

import tornado.simple_httpclient
import tornado.httpclient
import json
from pathvalidate import sanitize_filename, validate_filename

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
        :return:        Whether connection was successful.
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

            # response = await self.make_request("/")  # Default path "/"
            #
            # logger.info(str(response.code))
            # logger.info(response.body)

            return await self.fetch_server_content(controller)

        except tornado.simple_httpclient.HTTPTimeoutError:
             logger.error("Connection timed out.")
             self.disconnect_from_server(controller)
             return False

        except ValueError:
             logger.warning("Invalid ip-address or port given.")
             self.disconnect_from_server(controller)
             return False

        # except AttributeError:
        #      logger.warning("Failed to get response from server.")
        #      logger.debug()
        #      return False

        # Could not establish connection
        except ConnectionError:
            logger.warning("Failed to establish connection.")
            return False

    def disconnect_from_server(self, controller):
        """ Attempt to disconnect from server if connection is active

        :param controller:  Controller class of Application
        :return:            Whether disconnection was successful
        """
        if self.__session:
            self.__session.close()
            self.__session = None

        self.__server_url = None

        controller.update_filetree([])      # Empty filetree in GUI when not
                                            # connected
        return True

    async def make_request(self, path="/"):
        """
        Make a request to the server

        :param meth: Request method, compliant with HTTP/1.1
        :param path: url path to fetch.
        :return:     Response got from the server
        """
        if self.__session and self.__server_url:
            url = "%s%s" % (self.__server_url, path)
            #response = await self.__session.fetch(url)
            response = await self.__session.fetch(tornado.httpclient.HTTPRequest(url, "OPTIONS"))
            return response
        return None


    async def fetch_server_content(self, controller):
        """ Request server content and print it to view
        :param controller: Application Controller object
        :return: Whether fetching was successful
        """
        try:
            response = await self.make_request("/dir/")

            logger.info("Response status " + str(response.code))

            filenames = json.loads(response.body)

            san_names = []

            # Sanitize and validate filenames in provided in response
            # body before printing them out as possible downloads.
            for name in filenames:
                sname = sanitize_filename(name)
                try:
                    validate_filename(sname)
                    san_names.append(sname)
                except:
                    logger.warning("Ignoring invalid filename %s with index %i in response."
                                   % (sname, filenames.index(name)) )

            controller.update_filetree(san_names)
            return True

        except ValueError:
            logger.warning("Cannot parse response.")
            return False

        except tornado.httpclient.HTTPClientError:
            details, value, traceback = sys.exc_info()
            logger.info("Reason: %s" % value )
            return False

        except OSError:
            logger.error(sys.exc_info())
            return False

    async def fetch_file_from_server(self, filename, downloader):
        """ Request to download a file from server. """
        dl_url =  "/download/%s" % (filename)
        response = await self.make_request(dl_url)
        downloader.write_to_file(response.body)


