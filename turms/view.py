#   --- Turms ---
#   Class for handling printout and
#   data display to application GUI
#
#   Sipi Ylä-Nojonen, 2022

import asyncio
import queue
from queue import Empty
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog

import pathvalidate
from pathvalidate import sanitize_filename, validate_filename

from logger import TurmsLogger as Logger
from downloader import DEFAULT_DL_DIRECTORY

class ConsoleQueue:
    def __init__(self, queue_):
        """ Initiate with specified widget for print output """
        self._target = queue_

    def write(self, string):
        """ Write function for redirectiong sys.stdout writes to Tkinter application"""
        if self._target:
            self._target.put(string)

    def flush(self):
        pass

class ConsoleWriter:
    __listen = False
    _queue = None

    def __init__(self, widget):
        """ Initiate with specified widget for print output """
        self.__target = widget
        self._queue = queue.Queue()
        self.__listen = True

    async def start_listener(self):
        """ Start listening loop for GUI console output """
        self.__listen = True
        await self.listener()

    async def stop_listener(self):
        """ Stop listening for GUI console output """
        self.__listen = False

    async def listener(self):
        """ Write function for outputting logging data to Tkinter GUI console """
        while self.__listen:
            try:
                text = self._queue.get(block=False)

                if self.__target:
                    self.__target.insert_text(text)

            except Empty:
                await asyncio.sleep(0.2)              # Return other tasks when queue is empty

    def queue(self):
        """ Return queue for log output """
        return self._queue


class View(object):
    __window = None
    __widgets = {}
    __console = None
    __pipe = None

    def __init__(self, window, widgets):
        """ Initiates with specified widget for print output """
        self.__window = window
        self.__widgets = widgets

    def get_console(self, widget):
        """ Creates or return write stream console for application """
        if not self.__console and not self.__pipe:
            self.__console = ConsoleWriter(widget)
            self.__pipe = ConsoleQueue(self.__console.queue())
        return self.__pipe

    async def start_listener(self):
        """ Start printing out from GUI output queue. """
        await self.__console.start_listener()

    def stop_listener(self):
        """ Stop processing print out queue. """
        self.__console.stop_listener()

    def state_to_connect(self):
        """ Change GUI to show 'connected to server' state """
        # When user presses "Connect" button
        self.__widgets["connect"]["state"] = tk.DISABLED
        self.__widgets["disconnect"]["state"] = tk.NORMAL

    def state_to_disconnect(self):
        """ Change GUI to show 'not connected to server' state """
        # When user presses "Disconnect" button
        self.__widgets["connect"]["state"] = tk.NORMAL
        self.__widgets["disconnect"]["state"] = tk.DISABLED

    def state_to_server_running(self):
        """ Change GUI to show 'server running' state """
        self.__widgets["serverstop"]["state"] = tk.NORMAL
        self.__widgets["serverstart"]["state"] = tk.DISABLED

    def state_to_server_stopped(self):
        """ Change GUI to show 'server not running' state """
        self.__widgets["serverstart"]["state"] = tk.NORMAL
        self.__widgets["serverstop"]["state"] = tk.DISABLED

    def print_out_filetree(self, content):
        """
        Prints out list of filenames to application GUI filetree view

        :param content:     List of strings representing filenames
        :return:            None
        """
        tree = self.__widgets["filetree"]
        tree.delete(*tree.get_children())

        # Print out content to GUI
        for i, item in enumerate(content):
            try:
                validate_filename(item)                 # Check that print is a valid filename
                parsed = item
                tree.insert("", tk.END, value=parsed)
            except pathvalidate.ValidationError:
                Logger.warning("Ignoring invalid filename in response.")

    @staticmethod
    def prompt_save_location(filename):

        san_name = sanitize_filename(filename)

        # Validate filename by checking that name is within platform
        # length limits and sanitation was successful.
        validate_filename(san_name, platform="auto")
        splitname = san_name.split(".")
        extension = ""

        name = ""

        # File extension should be the last part in string split by "."
        # other parts are considered part of the filename.
        if len(splitname) >= 2:
            extension = splitname[-1]
            splitname.pop(-1)
            name = "".join(splitname)

        return tk.filedialog.asksaveasfilename(defaultextension=extension,
                                               initialdir=DEFAULT_DL_DIRECTORY,
                                               initialfile=name)

    @staticmethod
    def prompt_password():
        """ Prompt user for password to use."""
        return View.prompt_input("Please enter server password.", "*")

    @staticmethod
    def prompt_input(msg, show=""):
        """ Prompt user for string input.

        :param msg:     Message to prompt user with
        :param show:    Characters to show in place of input
        """
        return simpledialog.askstring(title="Server", prompt=msg, show=show)
