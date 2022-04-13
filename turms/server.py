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
DEFAULT_HOST = "127.0.0.1"     # Tornado HTTPServer expects address as string


#   -------------------------------------------------------
#   By default security features Tornado implements
#   include secure cookies, XSRF protection and
#   protection against DNS rebinding attacks.
#   https://www.tornadoweb.org/en/stable/guide/security.html
#
class TurmsApp(tornado.web.Application):

    # TODO: Check StaticFileHandler implementation and
    # TODO: Host name pattern against DNS rebound attack

    """ Tornado web application initialized for delegating request handling through HTTPServer class"""
    def __init__(self):
        handlers = [(r"/", rh.IndexRequestHandler),
                    (r"/dir/", rh.DirectoryRequestHandler)]
        settings = {"debug": True}
        super().__init__(handlers, **settings)


def create_server():
    """ Initialize server class object """
    return tornado.httpserver.HTTPServer(TurmsApp)


def start_server(server, port=DEFAULT_PORT, ip=DEFAULT_HOST):
    """ Initialize and start up server """
    asyncio.set_event_loop(asyncio.new_event_loop())
    server.listen(port, ip)
    return


def stop_server(server):
    """ Stop server running in separate thread """
    ioloop = tornado.ioloop.IOLoop.instance()
    logger.info("Server stopping.")
    asyncio.get_event_loop().create_task(server.close_all_connections())
    ioloop.add_callback(ioloop.stop)
    #ioloop.add_callback(ioloop.close)
    return


def start_server_thread(server, port, ip):
    import threading

    server_th = threading.Thread(target=start_server, args=[server, port, ip])
    server_th.daemon = True
    server_th.start()
    return server_th







