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

    """
    Tornado web application initialized for delegating request handling through HTTPServer class

    --- SECURITY NOTE ---
    Omit default_host argument from tornado.web.Application.__init__() as well as use appropriate
    host patterns in defining paths for application request handlers instead of r'.*'

    https://www.tornadoweb.org/en/stable/web.html#application-configuration
    """


    def __init__(self, host):
        handlers =  [ ( r"/", rh.IndexRequestHandler),
                        (r"/dir/", rh.DirectoryRequestHandler)]

            # [
            #         (HostMatches(host),
            #             [ ( r"/", rh.IndexRequestHandler),
            #             (r"/dir/", rh.DirectoryRequestHandler)]
            #          )
            #         ]
        settings = {"debug": True}
        super().__init__(handlers, **settings)

    def run(self, loop, port=DEFAULT_PORT, host="127.0.0.1"):
        """ Start up the server in asyncio event loop """
        logger.info("Starting server in port " + str(port))

        asyncio.set_event_loop(loop)
        self.__httpserver = self.listen(port)
        loop.run_forever()


    def stop(self, *args):
        """ Stop server by ending asyncio event loop """
        if self.__httpserver:
            self.__httpserver.stop()
            asyncio.get_event_loop().create_task(self.__httpserver.close_all_connections())
        logger.info("Server stopped.")
        return


def create_server(ip):
    """ Initialize server class object """
    app = TurmsApp(ip)
    return app # tornado.httpserver.HTTPServer(TurmsApp(ip))


def start_server(loop, server, port=DEFAULT_PORT, ip=DEFAULT_HOST):
    """ Initialize and start up server """

    # -- HTTPServer --
    # asyncio.set_event_loop(asyncio.new_event_loop())
    # logger.info("Starting server in %s:%s" % (ip, str(port)))
    # server.listen(port)
    # asyncio.get_event_loop().run_forever()
    # logger.info("Server started")

    server.run(loop, port, ip)

    return


def stop_server(loop, server):
    """ Stop server running in separate thread """

    # -- HTTPServer --
    # ioloop = tornado.ioloop.IOLoop.instance()
    # logger.info("Server stopping.")
    # asyncio.get_event_loop().call_soon_threadsafe(server.close_all_connections())
    # asyncio.get_event_loop().stop()
    # logger.info("Server stopped.")
    # #ioloop.add_callback(ioloop.close)

    logger.info("Server stopping.")
    asyncio.get_event_loop().call_soon_threadsafe(server.stop, loop)
    loop.stop()
    return


def start_server_thread(loop, server, port, ip):

    server_th = threading.Thread(target=start_server, args=[loop, server, port, ip])
    server_th.daemon = True
    server_th.start()
    return server_th







