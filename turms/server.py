#   --- Turms ---
#   Tornado based server for delegating
#   handlers for serving user requests.
#
#   Sipi Ylä-Nojonen, 2022
import sys

import request_handler as rh
from logger import TurmsLogger as Logger
from config import Config as cfg

import tornado.ioloop
import tornado.web
from tornado.web import HostMatches
import tornado.httpserver
import threading
import asyncio

#   By default use port that is unassigned by IANA
#   and not known to be widely used by other applications.
#   according to listing such as:
#       https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
#       https://www.speedguide.net/port.php?port=16568
DEFAULT_PORT = 16569
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
    __cfg = None
    __httpserver = None

    def __init__(self, port=DEFAULT_PORT, host=DEFAULT_HOST):
        """
        Tornado web application initialized for delegating request handling through HTTPServer class

        --- SECURITY NOTE ---
        Omit default_host argument from tornado.web.Application.__init__() as well as use appropriate
        host patterns in defining paths for application request handlers instead of r'.*'

        https://www.tornadoweb.org/en/stable/web.html#application-configuration

        :param port: Port to listen to when service is run
        :param host: Host name of server, define loopback options
        """

        # Prioritize initial values if available as: user supplied > config > default
        if port is DEFAULT_PORT:
            self.__port = int(cfg.get_server_val("Port", DEFAULT_PORT))
        else:
            self.__port = port

        if host is DEFAULT_HOST:
            self.__host = cfg.get_server_val("Host", DEFAULT_HOST)
        else:
            self.__host = host

        # Match host name with defined one to protect against DNS rebinding attacks.
        # This is the tornado.routing format version.
        # https://www.tornadoweb.org/en/stable/guide/security.html#dns-rebinding
        handlers = [(HostMatches(host), [(r"/", rh.IndexRequestHandler)]),
                    (HostMatches(host), [(r"/dir/", rh.DirectoryRequestHandler)]),
                    (HostMatches(host), [(r"/download/*.*", rh.FileRequestHandler)])]

        settings = {
            "xsrf_cookies": True                        # Prevent Cross site request forgery,
                                                        # Tornado web comes with built-in support
                                                        # for using XSRF-token.
                                                        # Technically this is unnecessary since application
                                                        # handlers only allow "HEAD" and "GET" methods
                                                        # So no server modification should be possible.

        }
        super().__init__(handlers, **settings)

    def run(self, loop):
        """
        Start up the server in asyncio.event_loop instance and
        start listening to connections in given port.

        :param loop Target event loop to use for executing
                    asynchronous server loop in.
        """
        Logger.info("Starting server in port " + str(self.__port))

        # asyncio.set_event_loop(loop)
        self.__httpserver = self.listen(self.__port, str(self.__host))
        # loop.run_forever()

    def stop(self, *args):
        """ Stop accepting new connections and await for all current
        connections to close and stop server application.
        """
        if self.__httpserver:
            self.__httpserver.stop()
            asyncio.get_event_loop().create_task(self.__httpserver.close_all_connections())
        Logger.info("Server stopped.")
        return

    def get_cfg(self):
        return self.__cfg


def create_server(port, host):
    """ Initialize server class object with given host address

    :param port: Port to listen to when service is run
    :param host: Host name of server, define loopback options
    """
    return TurmsApp(port, host)


def start_server(loop, app):
    """ Initialize and start up server

    :param loop: Asyncio event loop to pass on to server application
    :param app:  TurmsApp Application to run.
    """
    app.run(loop)
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


# --- TODO: Redundant, Moving server to asynchronous execution. ---
def start_server_thread(loop, app):
    """ Start TurmsApp application to run server in separate daemon thread.
    Call for "App.run()" with given parameters to set up asynchronous tornado
    server in daemon thread.

    :param loop Asyncio event loop to pass to function
    :param app  Application object to run
    """

    server_th = threading.Thread(target=start_server, args=[loop, app])
    server_th.daemon = True
    server_th.start()
    return server_th







