#   --- Turms ---
#   Controller class for delegating
#   user input to be processed
#
#   Sipi Ylä-Nojonen, 2022
import tornado.ioloop

import server
import connection_handler
import logger
import asyncio

class Controller:
    __view = None
    __app = None
    __window = None
    __conn_handler = None
    __server = None
    __server_handle = None  # Server thread

    def __init__(self, app, window, view):
        self.__app = app           # TODO: Weakref to avoid cyclic reference
        self.__window = window
        self.__view = view
        self.__conn_handler = connection_handler.ConnectionHandler()
        return

    async def connect_to_server(self, event):
        """ Attempt to connect to specified server. """

        ip = self.__app.widget("ip").get()
        port = self.__app.widget("port").get()

        if self.__conn_handler:
            success = await self.__conn_handler.connect_to_server(ip, port)

            if success:
                logger.info("Success")

            if success:
                self.__view.state_to_connection()

    async def disconnect_from_server(self, event):
        """ Disconnect connection from server. """

        if self.__conn_handler:
            success = self.__conn_handler.disconnect_from_server()
            if success:
                self.__view.state_to_disconnection()

    async def start_server(self, event):
        """ Create server if necessary and start it up. """
        if not self.__server:
            self.__server = server.create_server()

        self.__server_handle = server.start_server(self.__server)
        return

    async def stop_server(self, event):
        """ Stop server instance if it is running and join server thread """
        if self.__server:
            asyncio.create_task(self.__server.stop())
            if self.__server_handle:
                self.__server_handle.join()

    async def send_request(self, event):
        """ Send request to server """
        pass
