#   --- Turms ---
#   Tornado based server for delegating
#   handlers for serving user requests.
#
#   Sipi Ylä-Nojonen, 2022
import sys

import request_handler as rh
import logger

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

    # TODO: Check StaticFileHandler implementation and
    # TODO: Host name pattern against DNS rebound attack

    def __init__(self, host):
        """
        Tornado web application initialized for delegating request handling through HTTPServer class

        --- SECURITY NOTE ---
        Omit default_host argument from tornado.web.Application.__init__() as well as use appropriate
        host patterns in defining paths for application request handlers instead of r'.*'

        https://www.tornadoweb.org/en/stable/web.html#application-configuration

        :param host: Host name of server, define loopback options
        """
        handlers =  [ ( r"/", rh.IndexRequestHandler),
                        (r"/dir/", rh.DirectoryRequestHandler)]

            # [
            #         (HostMatches(host),
            #             [ ( r"/", rh.IndexRequestHandler),
            #             (r"/dir/", rh.DirectoryRequestHandler)]
            #          )
            #         ]
        settings = {}
        super().__init__(handlers, **settings)

    def run(self, loop, port=DEFAULT_PORT, host="127.0.0.1"):
        """
        Start up the server in asyncio.event_loop instance and
        start listening to connections in given port.

        :param loop Target event loop to use for executing
                    asynchronous server loop in.
        :param port Port to listen to for connections
        :param host Host-address to use, define loopback options
        """
        logger.info("Starting server in port " + str(port))

        asyncio.set_event_loop(loop)
        self.__httpserver = self.listen(port, host)
        loop.run_forever()


    def stop(self, *args):
        """ Stop accepting new connections and await for all current
        connections to close and stop server application.
        """
        if self.__httpserver:
            self.__httpserver.stop()
            asyncio.get_event_loop().create_task(self.__httpserver.close_all_connections())
        logger.info("Server stopped.")
        return


def create_server(ip):
    """ Initialize server class object with given host address """
    return TurmsApp(ip)


def start_server(loop, app, port=DEFAULT_PORT, ip=DEFAULT_HOST):
    """ Initialize and start up server

    :param loop: Asyncio event loop to pass on to server application
    :param app:  TurmsApp Application to run.
    :param port: Port to listen in for connections.
    :param ip:   Server host name to use.
    """
    app.run(loop, port, ip)
    return


def stop_server(loop, app):
    """ Stop server running in separate thread

    :param loop  Currently running asyncio.event_loop of target thread
    :param app   TurmsApp server handling application object
    """
    logger.info("Server stopping...")
    asyncio.get_event_loop().call_soon_threadsafe(app.stop, loop)
    loop.stop()
    return


def start_server_thread(loop, app, port, ip):
    """ Start TurmsApp application to run server in separate daemon thread.
    Call for "App.run()" with given parameters to set up asynchronous tornado
    server in daemon thread.

    :param loop Asyncio event loop to pass to function
    :param app  Application object to run
    :param port Port to pass to application function
    :param ip   Host name to pass to application function
    """

    server_th = threading.Thread(target=start_server, args=[loop, app, port, ip])
    server_th.daemon = True
    server_th.start()
    return server_th







