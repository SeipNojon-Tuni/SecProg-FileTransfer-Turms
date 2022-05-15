#   --- Turms ---
#   Tornado based server for delegating
#   handlers for serving user requests.
#
#   Sipi Ylä-Nojonen, 2022


import socket

import encrypt
import request_handler as rh
from logger import TurmsLogger as Logger
from config import Config as Cfg
from view import View

import tornado.ioloop
import tornado.web
from tornado.web import HostMatches
import tornado.httpserver
import asyncio

#   By default use port that is unassigned by IANA
#   and not known to be widely used by other applications.
#   according to listing such as:
#   https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
#   https://www.speedguide.net/port.php?port=16580
DEFAULT_PORT = 16580
DEFAULT_SSL_PORT = 16443
DEFAULT_HOST = socket.gethostbyname(socket.gethostname())


#   -------------------------------------------------------
#   Tornado supports security features, that
#   include secure cookies, XSRF protection and
#   protection against DNS rebinding attacks.
#   https://www.tornadoweb.org/en/stable/guide/security.html
#
class TurmsApp(tornado.web.Application):

    __host = DEFAULT_HOST
    __port = DEFAULT_PORT
    __httpserver = None
    __keyhold = None
    running = False

    def __init__(self):
        """
        Tornado web application initialized for delegating request handling through HTTPServer class

        --- SECURITY NOTE ---
        Omit default_host argument from tornado.web.Application.__init__() as well as use appropriate
        host patterns in defining paths for application request handlers instead of r'.*'

        https://www.tornadoweb.org/en/stable/web.html#application-configuration
        """

        # Get values from config or use defaults in case not present.
        self.__port = int(Cfg.get_turms_val("Port", DEFAULT_PORT))
        self.__sslport = int(Cfg.get_turms_val("SSLPort", DEFAULT_SSL_PORT))
        self.__host = Cfg.get_turms_val("Ip-Address", DEFAULT_HOST)

        # Match host name with defined one to protect against DNS rebinding attacks.
        # This is the tornado.routing format version.
        # https://www.tornadoweb.org/en/stable/guide/security.html#dns-rebinding
        handlers = [(HostMatches(self.__host), [(r"/", rh.IndexRequestHandler)]),
                    (HostMatches(self.__host), [(r"/dir/", rh.DirectoryRequestHandler)]),
                    (HostMatches(self.__host), [(r"/download/*.*", rh.FileRequestHandler)])]

        settings = {
            "xsrf_cookies": True                        # Prevent Cross site request forgery,
                                                        # Tornado web comes with built-in support
                                                        # for using XSRF-token.
                                                        # Technically this is unnecessary since application
                                                        # handlers only allow "HEAD" and "GET" methods
                                                        # So no server modification should be possible.
        }

        # Create encryption device factory
        if not Cfg.get_bool("TURMS", "AllowUnencrypted", False):
            self.__keyhold = encrypt.KeyHolder(View.prompt_input("Please enter encryption password.", "*"))
        # For unencrypted file transferring generate factory with
        # empty password. Rest is handled internally.
        else:
            self.__keyhold = encrypt.KeyHolder("")

        super().__init__(handlers, default_host=None, **settings)


    def run(self, timeout=3600):
        """
        Start up the server in asyncio.event_loop instance and
        start listening to connections in given port.

        :param timeout: Delay after which to shut down server.
        """

        # Set up TLS and start HTTPS server
        if Cfg.get_bool("TURMS", "UseTLS", True):
            # Load up SSL context to use for authenticating server
            # It still falls upon user to accept this authentication
            # and since we don't authenticate user and thus anyone
            # can download content, the encryption of server files
            # upon sending is actually the only thing keeping them
            # secret.
            # Problem is tornado client doesn't have an easy way of
            # accessing the certificate and it is handled inside the
            # ssl socket and we can't show it to client of manual
            # inspection.
            try:
                password = encrypt.KeyGen.generate_cert_chain()
            except TypeError as e:
                del password
                Logger.error(e)
                return
            except ValueError as ex:
                del password
                Logger.error(ex)
                return

            ssl_ctx = encrypt.KeyGen.get_context(password)

            # Remove so it won't be accessed later
            del password

            # Start up HTTPS server
            if ssl_ctx:
                self.__httpserver = tornado.httpserver.HTTPServer(self, ssl_options=ssl_ctx)
                Logger.info("Starting HTTPS server in %s:%s" % (str(self.__host), str(self.__sslport)))
                self.__httpserver.listen(self.__sslport, str(self.__host))
                self.running = True
                asyncio.get_event_loop().create_task(self.server_timeout(timeout))
                return
            else:
                Logger.error("Cannot start server: server is configured to use HTTPS but no SSL context was found.")
                return

        # Start up HTTP server.
        else:
            self.__httpserver = tornado.httpserver.HTTPServer(self)
            Logger.info("Starting HTTP server in  %s:%s" % (str(self.__host), str(self.__port)))
            self.__httpserver.listen(self.__port, str(self.__host))
            self.running = True
            asyncio.get_event_loop().create_task(self.server_timeout(timeout))
            return

    def stop(self, *args):
        """ Stop accepting new connections and await for all current
        connections to close and stop server application.
        """
        if self.__httpserver:
            self.__httpserver.stop()
            asyncio.get_event_loop().create_task(self.__httpserver.close_all_connections())
        Logger.info("Server stopped.")
        self.running = False
        return

    async def server_timeout(self, time=3600):
        """ Call for server to shutdown after delay

        :param time:    Timeout delay
        """
        # Asyncio sleep is in seconds (default 3600s=1h)
        await asyncio.sleep(time)
        Logger.info("Server timed out, stopping server...")
        self.stop()
        return

    def get_encryptor(self):
        # Recreate encryptor when new reference to it is made.
        return self.__keyhold.create_encryptor()





