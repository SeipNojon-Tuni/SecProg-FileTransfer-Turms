#   --- Turms ---
#   Class for handling printout and
#   data display to application GUI
#
#   Sipi Ylä-Nojonen, 2022
import logging
import tkinter as tk

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
        """ Initiate with specified widget for print output """
        self.__window = window
        self.__widgets = widgets

    def get_console(self, widget):
        """ Create or return write stream console for application """
        if not self.__console:
            self.__console = Console(widget)
        return self.__console

    def state_to_connection(self):
        # When user presses "Connect" button
        self.__widgets["connect"]["state"] = tk.DISABLED
        self.__widgets["disconnect"]["state"] = tk.NORMAL

    def state_to_disconnection(self):
        # When user presses "Disconnect" button
        self.__widgets["connect"]["state"] = tk.NORMAL
        self.__widgets["disconnect"]["state"] = tk.DISABLED



