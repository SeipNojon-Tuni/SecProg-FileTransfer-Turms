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

    def __init__(self, app, view):
        self.__app = weakref.ref(app)           # Avoid cyclic referencing
        self.__view = view
        return


    async def connect_to_server(self, server_addr, port=server.DEFAULT_PORT):
        """
        Attempt to connect to specified server
        :param server_addr : Address to connect to. Should be valid ip-address.
        :param port : Server port to attempt to connect to.

        """

        pass


    async def send_request(self):
        """ Send request to server """
        pass
