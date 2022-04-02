#   --- Turms ---
#   Application framework implementation
#
#   Sipi Ylä-Nojonen, 2022

import console_widget
import tkinter as tk
import tkinter.ttk as ttk
import controller as ctrl

class App():

    __window = None
    __controller = None
    __widgets = {}

    def __init__(self):
        return

    def run(self):
        """
        Run through app initialization actions
        such as creating window and controllers for
        application.
        """

        # Create tkinter window for app and
        # controller object for input handling.
        self.__window = self.create_window()
        self.__controller = ctrl.Controller(self, self.__window)
        self.__window.mainloop()


    def create_window(self):
        """
        Create tkinter window to serve as
        GUI for the application and setup
        elements for the window.

        :return: Created window.
        """

        # Window size and name settings
        window = tk.Tk()
        window.geometry("640x400")
        window.minsize(640, 400)
        window.title("Turms File Transfer")
        window.iconphoto(False, tk.PhotoImage(file="icon.png"))

        # Main frame container
        mframe = tk.Frame(window)
        mframe.grid(row=0, column=0)

        # Left side frame
        lframe = tk.Frame(mframe)
        lframe.grid(row=0, column=0)

        # Right side frame
        rframe = tk.Frame(mframe)
        rframe.grid(row=0, column=1)

        # Filetree view


        # Console window and
        console = console_widget.Console(master=lframe)
        console.grid(row=0, column=0, padx=2, pady=1)


        # Ip-address / port inputs

        # Connect button / disconnect button


        self.__widgets["mframe"] = mframe
        self.__widgets["console"] = console

        return window

