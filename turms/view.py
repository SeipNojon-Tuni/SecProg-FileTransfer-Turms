#   --- Turms ---
#   Class for handling printout and
#   data display to application GUI
#
#   Sipi Ylä-Nojonen, 2022
import cgi
import logging
import tkinter as tk
from tkinter import filedialog
from pathvalidate import sanitize_filename, validate_filename

from downloader import DEFAULT_DL_DIRECTORY

class Console:
    def __init__(self, widget):
        """ Initiate with specified widget for print output """
        self._target = widget

    def write(self, string):
        """ Write function for redirectiong sys.stdout writes to Tkinter application"""
        if self._target:
            self._target.insert_text(string)
        else:
            logging.getLogger("turms.logger")\
                .log(level=logging.WARNING, msg="No output for Tkinter GUI logging specified.")

    def flush(self):
        pass


class View(object):
    __window = None
    __widgets = {}
    __console = None

    def __init__(self, window, widgets):
        """ Initiates with specified widget for print output """
        self.__window = window
        self.__widgets = widgets

    def get_console(self, widget):
        """ Creates or return write stream console for application """
        if not self.__console:
            self.__console = Console(widget)
        return self.__console

    def state_to_connect(self):
        # When user presses "Connect" button
        self.__widgets["connect"]["state"] = tk.DISABLED
        self.__widgets["disconnect"]["state"] = tk.NORMAL

    def state_to_disconnect(self):
        # When user presses "Disconnect" button
        self.__widgets["connect"]["state"] = tk.NORMAL
        self.__widgets["disconnect"]["state"] = tk.DISABLED

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
            # TODO: Escape dangerous characters
            # TODO: +++++++++++++++++++++++++++
            parsed = item
            # TODO: +++++++++++++++++++++++++++
            tree.insert("", tk.END, value=parsed)

    def prompt_save_location(self, filename):

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


        return tk.filedialog.asksaveasfilename(defaultextension=extension, initialdir=DEFAULT_DL_DIRECTORY, initialfile=name)


