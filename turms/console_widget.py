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