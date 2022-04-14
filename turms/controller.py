#   --- Turms ---
#   Controller class for delegating
#   user input to be processed
#
#   Sipi Ylä-Nojonen, 2022
import threading

import tornado.ioloop

import server
import connection_handler
import logger
import asyncio
import tornado.gen


class Controller:
    __view = None
    __app = None
    __window = None
    __conn_handler = None
    __server = None
    __server_handle = None
    __server_loop = None

    def __init__(self, app, window, view):
        self.__app = app           # TODO: Weakref to avoid cyclic reference
        self.__window = window
        self.__view = view
        self.__conn_handler = connection_handler.ConnectionHandler()
        return

    async def connect_to_server(self, event):
        """ Attempt to connect to specified server. """

        self.state_to_connect()
        ip = self.__app.widget("ip").get()
        port = self.__app.widget("port").get()

        if self.__conn_handler:
            succ = await self.__conn_handler.connect_to_server(ip, port, self)

    async def disconnect_from_server(self, event):
        """ Disconnect connection from server. """

        if self.__conn_handler:
            self.__conn_handler.disconnect_from_server(self)

    async def start_server(self, event):
        """ Create server if necessary and start it up. """
        ip = "127.0.0.1"

        # Join server thread to ensure we can set up server again.
        # This is done here because calling join when stopping the server
        # will block async loop and deadlock.
        # ---
        # For this server thread is also flagged as daemon and will
        # thus be killed along the main thread when program exits.
        if self.__server_handle:
            self.__server_handle.join()

        if not self.__server:
            self.__server = server.create_server(ip)
            self.__server_loop = asyncio.new_event_loop()

        self.__server_handle = server.start_server_thread(self.__server_loop, self.__server, server.DEFAULT_PORT, ip)
        return

    async def stop_server(self, event):
        """ Stop server instance if it is running and join server thread """
        if self.__server:
            server.stop_server(self.__server_loop, self.__server)

    async def send_request(self, event):
        """ Send request to server """
        pass

    def state_to_connect(self):
        self.__view.state_to_connect()

    def state_to_disconnect(self):
        self.__view.state_to_disconnect()

    def update_filetree(self, items):
        self.__view.print_out_filetree(items)
