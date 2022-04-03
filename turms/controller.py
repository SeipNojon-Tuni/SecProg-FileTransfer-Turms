#   --- Turms ---
#   Controller class for delegating
#   user input to be processed
#
#   Sipi Ylä-Nojonen, 2022

import server
import connection_handler
import tkinter
import asyncio
import weakref
import requests

class Controller():
    __view = None
    __app = None
    __conn_handler = None

    def __init__(self, app, view):
        self.__app = app           # TODO: Weakref to avoid cyclic reference
        self.__view = view
        self.__conn_handler = connection_handler.ConnectionHandler()
        return


    async def connect_to_server(self, event):
        """
        Attempt to connect to specified server
        :param server_addr : Address to connect to. Should be valid ip-address.
        :param port : Server port to attempt to connect to.

        """

        ip = self.__app.widget("ip").get()
        port = self.__app.widget("port").get()

        if self.__conn_handler:
            self.__conn_handler.connect_to_server(ip, port)



    async def disconnect_from_server(self, event):
        if self.__conn_handler.active_connection():
            self.__conn_handler.disconnect_from_server()


    async def send_request(self, event):
        """ Send request to server """
        pass
