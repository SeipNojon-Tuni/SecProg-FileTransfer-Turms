#   --- Turms ---
#   Controller class for delegating
#   user input to be processed
#
#   Sipi Ylä-Nojonen, 2022

import server
import connection_handler
from pyglet.window import mouse
import asyncio

class Controller():
    __view = None

    def __init__(self, view):
        self.__view = view
        self.map_events()
        return

    def map_events(self):
        """ Map events from pyglet window for handling by controller """

        window = self.__view

        @window.event
        def on_mouse_press(x, y, button, arg):
            if button == mouse.LEFT:
                print("LMB")
            elif button == mouse.RIGHT:
                print("RMB")

        @window.event
        def on_key_press(symbol, modifiers):
            print("key pressed")



    def connect_to_server(self, server_addr, port=server.DEFAULT_PORT):
        """
        Attempt to connect to specified server
        :param server_addr : Address to connect to. Should be valid ip-address.
        :param port : Server port to attempt to connect to.

        """

        pass

    def send_request(self):
        """ Send request to server """
        pass
