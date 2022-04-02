#   --- Turms ---
#   Tkinter multiline text widget with
#   scrollbar
#
#   Sipi Ylä-Nojonen

import tkinter as tk
from tkinter import scrolledtext

class Console(scrolledtext.ScrolledText):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def insert_text(self, text, ending=""):
        """
        Insert given text into entry in GUI

        :param text, string content of text to input
        :param ending, string line ending for text content

        :return None
        """

        self.insert(tk.END, text + ending)
        self.see(tk.END)
        return

    def erase_row(self):
        """ Erase the last row of text """
        self.delete("end-1l", "end")  # linestart+1c
        self.insert(tk.END, "\n")

    def replace_text(self, text, start=0, end=tk.END):
        """
        Replace GUI entry text with given. defaults to all

        :param text, string content of text to input
        :param start, Start index of replacing
        :param end, Ending index of replacing

        :return None
        """

        self.delete(start, end)
        self.insert(end, text)

        return