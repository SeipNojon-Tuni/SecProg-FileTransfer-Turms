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
import tornado.httpserver
import threading
import asyncio

#   By default use port that is unassigned by IANA
#   and not known to be widely used by other applications.
#   according to listing such as:
#       https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
#       https://www.speedguide.net/port.php?port=16568
DEFAULT_PORT = 16569


#   -------------------------------------------------------
#   By default security features Tornado implements
#   include secure cookies, XSRF protection and
#   protection against DNS rebinding attacks.
#   https://www.tornadoweb.org/en/stable/guide/security.html
#
class TurmsServer(tornado.web.Application):
    __httpserver = None

    """ Tornado web application Server for delegating user requests"""
    def __init__(self):
        handlers = [ (r"/", rh.TurmsRequestHandler) ]
        settings = {"debug": True}
        super().__init__(handlers, **settings)

    def run(self, port=DEFAULT_PORT):
        """ Start up the server in asyncio event loop """
        logger.info("Starting server in port " + str(port))
        self.__httpserver = self.listen(port)
        if not asyncio.get_event_loop().is_running():
            tornado.ioloop.IOLoop.instance().start()

    async def stop(self):
        """ Stop server by ending asyncio event loop """
        if self.__httpserver:
            await self.__httpserver.close_all_connections()
        tornado.ioloop.IOLoop.instance().stop()
        logger.info("Server stopped.")
        return


def create_server():
    """ Initialize server class object """
    return TurmsServer()


def start_server(server):
    """ Initialize and start up server """
    asyncio.set_event_loop(asyncio.new_event_loop())
    server.run()
    return


def start_server_thread(server):
    """ Initialize server thread """
    # Start server in new thread
    server_thread = threading.Thread(target=start_server, args=[server])
    server_thread.daemon = True
    server_thread.start()

    return server_thread


def stop_server():
    """ Stop server running in separate thread """
    pass




