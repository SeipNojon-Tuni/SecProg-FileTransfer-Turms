#   --- Turms ---
#   Controller class for delegating
#   user input to be processed
#
#   Sipi Ylä-Nojonen, 2022

import downloader
import server
import connection_handler
import view
from logger import TurmsLogger as Logger
import asyncio
from pathvalidate import validate_filename, sanitize_filename

class Controller:

    __view = None
    __app = None
    __window = None
    __conn_handler = None
    __server = None

    def __init__(self, widgets, window, view):
        """:type Controller: Turms Application controller class
        that loosely follows controller functionality of MVC-pattern

        :param widgets  Dictionary of Application widgets and fields to read input from
                        or pass to View for GUI handling and manipulation
        :param window
        :param view     MVC type View object responsible for updating GUI.
        """

        self.__widgets = widgets
        self.__window = window
        self.__view = view
        self.__conn_handler = connection_handler.ConnectionHandler()
        return

    async def connect_to_server(self, event):
        """ Delegate to create ConnectionHandler instance and for it to
        attempt to connect to specified server. Values for server host address and
        port are read from GUI input fields specified by dictionary passed in
        initiation of current Controller object.

        :param event: Tkinter event fired when action to call function was taken
        """

        self.state_to_connect()             # Called already here so input fields can be
                                            # locked before reading values.
        ip = self.__widgets["ip"].get()
        port = self.__widgets["port"].get()

        if self.__conn_handler:
            await self.__conn_handler.connect_to_server(ip, port, self)

    async def disconnect_from_server(self, event):
        """ Delegate for ConnectionHandler instance to close connection to server if connected.

        :param event: Tkinter event fired when action to call function was taken
        """
        success = False

        if self.__conn_handler:
            success = self.__conn_handler.disconnect_from_server(self)

    async def fetch_file_from_server(self, event):
        """ Request to fetch specified file from server """

        try:
            focus = self.__widgets["filetree"].focus()
            filename = self.__widgets["filetree"].item(focus)["values"][0]

            # Sanitize filename by replacing invalid characters with "" and
            # adding underscore to filename if it is a name reserved by system.
            san_name = sanitize_filename(filename)

            # Validate filename by checking that name is within platform
            # length limits and sanitation was successful.
            validate_filename(san_name)

            location = view.View.prompt_save_location(san_name)

            # User cancelled action.
            if location == "":
                return

            Logger.info("Requesting file %s. " % san_name)

            # Downloader class sanitizes and validates download destination internally.
            #   Raises pathvalidate.ValidationError if validation is not successful.
            download = downloader.Downloader(location)

            await self.__conn_handler.fetch_file_from_server(san_name, download, self)
        # User clicked on non-existent item in tree.
        except IndexError:
            Logger.warning("Unknown item.")
            return

        # except pathvalidate.ValidationError:
        #     detail, value, traceback = sys.exc_info()
        #     logger.error("Invalid file path %s" % value)
        #     return

    async def start_server(self, event):
        """ Delegate to create instance of TurmsApp application and to
        start it up in daemon thread.

        :param event:   Tkinter event fired when action to call function was taken
        :return:        None
        --------------------------------------------------------------
        Note:
            # Joining server thread is done here because calling
            # 'threading.Thread.join()' when stopping the server would
            # block async loop and prevent finishing execution.
            # Calling with timeout at shutdown would also block and finally kill
            # thread every time without actually finishing execution of the loop.
            #
            # Server thread is also flagged as daemon and will thus
            # be killed along the main thread when program exits.

        """

        if not self.__server:
            try:
                self.__server = server.TurmsApp()
            # Password missing when encryption is required may raise ValueError
            except ValueError as e:
                Logger.error(e)
                return
            self.__server.run()
            self.state_to_server_running()
        else:
            Logger.error("Can't start a server. Server is already running.")
        return

    async def stop_server(self, event):
        """ Call for server to stop accepting new connections, close all existing ones and exit. """
        if self.__server:
            self.__server.stop()
            del self.__server
            self.state_to_server_stopped()

    def state_to_connect(self):
        """ Delegate for View to change GUI state to being connected to server """
        self.__view.state_to_connect()

    def state_to_disconnect(self):
        """ Delegate for View to change GUI state to not being connected to server """
        self.__view.state_to_disconnect()

    def state_to_server_running(self):
        """ Delegate for View to change GUI state to server running """
        self.__view.state_to_server_running()

    def state_to_server_stopped(self):
        """ Delegate for View to change GUI state to server not running """
        self.__view.state_to_server_stopped()

    def update_filetree(self, items):
        """ Delegate for View to printout details if given file list to GUI """
        self.__view.print_out_filetree(items)

    @staticmethod
    def prompt_password():
        return view.View.prompt_password()

