#   --- Turms ---
#   Handler for making requests from client to server
#   and delegating answers
#
#   Sipi Ylä-Nojonen, 2022
import sys
from ipaddress import ip_address
import base64
import asyncio

from logger import TurmsLogger as Logger
from config import Config as cfg

import tornado.simple_httpclient
import tornado.httpclient
import json
from pathvalidate import sanitize_filename, validate_filename


class ConnectionHandler:
    __session = None
    __server_url = None
    __cookies = None
    __decryptor = None

    def __init__(self):
        pass

    async def connect_to_server(self, ipaddr, port, controller):
        """
        Attempt to create a connection to specified server.

        :param ipaddr:  Address of the server. Should be valid ip-address.
        :param port:    Port to attempt to send the request.
        :return:        Whether connection was successful.
        """

        # Allow connection only when no former connection is active.
        if self.__session or self.__server_url:
            Logger.info("Already connected to a server. Please terminate connection first.")
            return

        try:
            ip = ip_address(ipaddr)                     # Raises ValueError if not valid IPv4 or IPv6 address
            portint = int(port)
        except ValueError:
            Logger.warning("Invalid ip-address or port given.")
            self.disconnect_from_server(controller)
            return False

        try:
            url = "https://%s:%s" % (ipaddr, portint)

            self.__server_url = url
            self.__session = tornado.httpclient.AsyncHTTPClient()

            Logger.info("Connecting to " + url)

            await self.initial_request()

            return await self.fetch_server_content(controller)

        except tornado.simple_httpclient.HTTPTimeoutError:
            Logger.error("Connection timed out.")
            self.disconnect_from_server(controller)
            return False

        # Could not establish connection
        except ConnectionError:
            Logger.warning("Failed to establish connection.")
            self.disconnect_from_server(controller)
            return False

    def disconnect_from_server(self, controller):
        """ Attempt to disconnect from server if connection is active
        and clean up connection objects and filetree in View.

        :param controller:  Controller class of Application
        :return:            Whether disconnection was successful
        """
        if self.__session:
            self.__session.close()
            self.__session = None

        self.__decryptor = None
        self.__server_url = None

        controller.update_filetree([])  # Empty filetree in GUI when not connected
        controller.state_to_disconnect()

        return True

    async def get_request(self, path="/"):
        """
        Make a GET request to the server

        :param path: url path to fetch.
        :return:     Response got from the server
        """
        if self.__session and self.__server_url:
            url = "%s%s" % (self.__server_url, path)

            # Don't validate certificate since server certificate is self-signed and validation will fail.
            request = tornado.httpclient.HTTPRequest(url, method="GET", validate_cert=False)
            response = await self.__session.fetch(request)
            return response
        return None

    async def initial_request(self):
        """ Send initial request and create connection to server,
        set necessary tokens etc.
        """
        if self.__session and self.__server_url:
            url = "%s%s" % (self.__server_url, "/")

            # Don't validate certificate since server certificate is self-signed and validation will fail.
            request = tornado.httpclient.HTTPRequest(url, "GET", validate_cert=False)
            response = await self.__session.fetch(request)

            try:
                self.__cookies = response.headers["Set-Cookie"]
            except KeyError:
                self.__cookies = None

            return response
        return

    async def fetch_server_content(self, controller):
        """ Request server content and print it to view
        :param controller: Application Controller object
        :return: Whether fetching was successful
        """
        try:
            response = await self.get_request("/dir/")

            if not response:
                Logger.error("Could not parse response.")
                return False

            Logger.info("Response: %s %s " % ( str(response.code), response.reason) )

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
                    Logger.warning("Ignoring invalid filename %s with index %i in response."
                                   % (sname, filenames.index(name)) )

            controller.update_filetree(san_names)
            return True

        except tornado.httpclient.HTTPClientError:
            type, value, traceback = sys.exc_info()
            Logger.warning("%s" % value)
            return False

        except OSError:
            type, value, trace = sys.exc_info()
            Logger.error(value)
            return False

    async def fetch_file_from_server(self, filename, downloader, controller):
        """ Request to download a file from server. """

        try:
            dl_url = "/download/%s" % filename

            response = await self.get_request(dl_url)

            salt = b""
            iv = b""
            checksum = b""

            try:
                checksum = base64.urlsafe_b64decode(response.headers["checksum"])
                salt = base64.urlsafe_b64decode(response.headers["salt"])
                iv = base64.urlsafe_b64decode(response.headers["iv"])
            except KeyError:
                Logger.error("Error parsing response headers. Header not present.")

            downloader.create_decryptor(controller.prompt_password(), salt, iv)

            if not response:
                Logger.error("Could not parse response.")
                return

            Logger.info("Response: %s %s " % (str(response.code), response.reason))

            # Decrypt server response if necessary and write content to file.
            data = response.body
            if response.headers["encrypted"] == "True":
                downloader.decrypt_and_write(data)
            else:
                downloader.write_to_file(data)
            await asyncio.sleep(0.01)

            Logger.info("Finished downloading.")

            if downloader.compare_checksum(checksum):
                Logger.info("File integrity check passed.")
            else:
                Logger.warning("File integrity check failed. File might be damaged.")
                if cfg.get_bool("TURMS", "AutoRemoveDamagedFile"):
                    downloader.remove_file()

        except tornado.httpclient.HTTPClientError:
            t, value, traceback = sys.exc_info()
            Logger.warning("%s" % value)
            return False

        except ConnectionRefusedError:
            Logger.error("Server refused connection.")


