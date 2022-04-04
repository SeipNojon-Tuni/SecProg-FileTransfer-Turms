#   --- Turms ---
#   Class for handling printout and
#   data display to application GUI
#
#   Sipi Ylä-Nojonen, 2022
import logging


class View(object):
    _target = None

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