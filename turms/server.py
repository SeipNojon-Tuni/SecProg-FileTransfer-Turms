#   --- Turms ---
#   Tornado based server for delegating
#   handlers for serving user requests.
#
#   Sipi Ylä-Nojonen, 2022


import encrypt
import request_handler as rh
from logger import TurmsLogger as Logger
from config import Config as cfg
import view

import tornado.ioloop
import tornado.web
from tornado.web import HostMatches
import tornado.httpserver
import asyncio

#   By default use port that is unassigned by IANA
#   and not known to be widely used by other applications.
#   according to listing such as:
#       https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
#       https://www.speedguide.net/port.php?port=16568
DEFAULT_PORT = 16569
DEFAULT_SSL_PORT = 16443
DEFAULT_HOST = "127.0.0.1"


#   -------------------------------------------------------
#   By default security features Tornado implements
#   include secure cookies, XSRF protection and
#   protection against DNS rebinding attacks.
#   https://www.tornadoweb.org/en/stable/guide/security.html
#
class TurmsApp(tornado.web.Application):

    __host = DEFAULT_HOST
    __port = DEFAULT_PORT
    __httpserver = None
    __keyhold = None

    def __init__(self):
        """
        Tornado web application initialized for delegating request handling through HTTPServer class

        --- SECURITY NOTE ---
        Omit default_host argument from tornado.web.Application.__init__() as well as use appropriate
        host patterns in defining paths for application request handlers instead of r'.*'

        https://www.tornadoweb.org/en/stable/web.html#application-configuration
        """

        # Get values from config or use defaults in case not present.
        self.__port = int(cfg.get_turms_val("Port", DEFAULT_PORT))
        self.__sslport = int(cfg.get_turms_val("SSLPort", DEFAULT_SSL_PORT))
        self.__host = cfg.get_turms_val("Host", DEFAULT_HOST)

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
        self.__keyhold = encrypt.KeyHolder(view.View.prompt_password())

        super().__init__(handlers, **settings)

    def run(self):
        """
        Start up the server in asyncio.event_loop instance and
        start listening to connections in given port.
        """

        # Set up TLS and start HTTPS server
        if cfg.get_bool("TURMS", "UseTLS"):
            # Load up SSL context to use for authenticating server
            # It still falls upon user to accept this authentication
            # and since we don't authenticate user and thus anyone
            # can download content, the encryption of server files
            # upon sending is actually the only thing keeping them
            # secret.
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

            # Shouldn't be needed after this
            del password

            if ssl_ctx:
                self.__httpserver = tornado.httpserver.HTTPServer(self, ssl_options=ssl_ctx)
                Logger.info("Starting HTTPS server in port " + str(self.__sslport))
                self.__httpserver.listen(self.__sslport, str(self.__host))
            else:
                Logger.error("Cannot start server: server is configured to use HTTPS but no SSL context was found.")
                return
        # Start up HTTP server.
        else:
            self.__httpserver = tornado.httpserver.HTTPServer(self)
            Logger.info("Starting HTTP server in port " + str(self.__port))
            self.__httpserver.listen(self.__port, str(self.__host))
            return

    def stop(self, *args):
        """ Stop accepting new connections and await for all current
        connections to close and stop server application.
        """
        if self.__httpserver:
            self.__httpserver.stop()
            asyncio.get_event_loop().create_task(self.__httpserver.close_all_connections())
        Logger.info("Server stopped.")
        return

    def get_encryptor(self):
        # Recreate encryptor when new reference to it is made.
        return self.__keyhold.create_encryptor()


def create_server():
    """ Initialize server class object with given host address """
    return TurmsApp()


def start_server(app):
    """ Initialize and start up server

    :param app:  TurmsApp Application to run.
    """
    app.run()
    return


def stop_server(loop, app):
    """ Stop server running in separate thread

    :param loop  Currently running asyncio.event_loop of target thread
    :param app   TurmsApp server handling application object
    """
    Logger.info("Server stopping...")
    asyncio.get_event_loop().call_soon_threadsafe(app.stop, loop)
    loop.stop()
    return







