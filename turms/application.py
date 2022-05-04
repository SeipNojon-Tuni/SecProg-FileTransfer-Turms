#   --- Turms ---
#   Application framework implementation
#
#   Sipi Ylä-Nojonen, 2022
import logging
import sys
import tkinter as tk
import tkinter.ttk as ttk
import asyncio

import config
import console_widget
import controller as ctrl
from logger import TurmsLogger as Logger
import server
import view


def call_async(target):
    """ Fire and forget application events by creating new asyncio event_loop
    when necessary and queueing functions for asynchronous execution.

    Either create new task with 'asyncio.get_event_loop().create_task()' or
    if a loop is already running or start up a new loop and start execution
    of first function with 'asyncio.get_event_loop.run_until_complete()'.

    Expect function to return after execution finishes, but
    omit possible returned 'Future' object.

    :param target : Target asynchronous function to be executed.
    """
    # Create new event loop if necessary and add the new coroutine to loop.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.new_event_loop()
    finally:
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.run_until_complete(target)
        else:
            loop.create_task(target)


class App:

    __window = None
    __gui_pipeline = None
    __controller = None
    __widgets = {}
    __run = False

    async def run(self):
        """ Run through app initialization actions
        of creating window and controllers for
        application.
        """

        # Create tkinter window for app and
        # controller object for input handling.
        self.__window = self.create_window()
        self.__view = view.View(self.__window, self.__widgets)
        self.__controller = ctrl.Controller(self.__widgets, self.__window, self.__view)

        # Create loggers
        self.__gui_pipeline = self.__view.get_console(self.__widgets["console"])
        sys.stdout = self.__gui_pipeline

        call_async(self.__view.start_listener())

        Logger.create_logger()
        Logger.info("--- Application initialization finished. ---")
        Logger.set_log_level(logging.DEBUG)

        self.__run = True
        await self.async_mainloop()

    def create_window(self):
        """ Create tkinter window to serve as
        GUI for the application and setup
        elements for the window.

        :return: Created window.
        """

        # Window size and name settings
        window = tk.Tk()
        window.minsize(1280, 500)
        window.title("Turms File Transfer")
        window.iconphoto(False, tk.PhotoImage(file="icon.png"))
        window.geometry("1400x500")

        # -- Right side frame --
        rframe = tk.Frame(window)
        rframe.grid(row=0, column=1)

        # -- Console window and prompt -- Left side
        console = console_widget.Console(master=window)
        console.grid(row=0, column=0, padx=2, pady=1, sticky="NSEW")

        # -- Filetree view -- Right side
        filetree = ttk.Treeview(rframe, columns=["filename", "filesize"])
        filetree.grid(row=0, column=0, padx=1, pady=1, columnspan=3, sticky="N")
        filetree.heading("filename", text="File name")
        filetree.heading("filesize", text="File size")

        # -- Ip-address/port labels/input --
        ip_label = ttk.Label(master=rframe, text="IP-address")
        ip_label.grid(row=1, column=0, padx=1, pady=2, columnspan=2, sticky="E")
        ip_addr = ttk.Entry(rframe)
        ip_addr.grid(row=2, column=0, padx=1, pady=2, columnspan=2, sticky="E")

        port_label = ttk.Label(master=rframe, text="Port")
        port_label.grid(row=3, column=0, padx=1, pady=2, columnspan=2, sticky="E")
        port = ttk.Entry(rframe)
        port.grid(row=4, column=0, padx=1, pady=2, columnspan=2, sticky="E")

        ip_addr.insert(tk.END, server.DEFAULT_HOST)
        port.insert(tk.END, str(server.DEFAULT_PORT))

        # -- Connect button / disconnect button --
        c_button = ttk.Button(master=rframe, text="Connect")
        dc_button = ttk.Button(master=rframe, text="Disconnect", state="disabled")
        c_button.grid(row=2, column=2, padx=2, pady=2, columnspan=2, sticky="E")
        dc_button.grid(row=4, column=2, padx=2, pady=2, columnspan=2, sticky="E")

        s_button = ttk.Button(master=rframe, text="Start Server")
        s_button.grid(row=5, column=0, padx=2, pady=2, columnspan=2, sticky="E")

        sstop_button = ttk.Button(master=rframe, text="Stop Server")
        sstop_button.grid(row=5, column=2, padx=2, pady=2, columnspan=2, sticky="E")

        # -- Dictionary of widgets --
        self.__widgets["console"] = console
        self.__widgets["connect"] = c_button
        self.__widgets["disconnect"] = dc_button
        self.__widgets["ip"] = ip_addr
        self.__widgets["port"] = port
        self.__widgets["filetree"] = filetree

        self.__widgets["serverstart"] = s_button
        self.__widgets["serverstop"] = sstop_button

        # Action bindings to Controller
        c_button.bind("<Button-1>", lambda event: call_async(self.__controller.connect_to_server(event)))
        dc_button.bind("<Button-1>", lambda event: call_async(self.__controller.disconnect_from_server(event)))
        s_button.bind("<Button-1>", lambda event: call_async(self.__controller.start_server(event)))
        sstop_button.bind("<Button-1>", lambda event: call_async(self.__controller.stop_server(event)))
        filetree.bind("<Double-1>", lambda event: call_async(self.__controller.fetch_file_from_server(event)))

        # On closing window / program
        window.protocol("WM_DELETE_WINDOW", self.on_window_exit)

        window.grid_columnconfigure(0, minsize=1000, weight=2)
        window.grid_columnconfigure(0, minsize=400, weight=1)

        return window

    async def async_mainloop(self):
        """ Asynchronous version of tkinter.Tk.mainloop()"""
        while self.__run:
            self.__window.update()
            await asyncio.sleep(0.01)

    def widget(self, name):

        return self.__widgets[name]

    def on_window_exit(self):
        Logger.info("Program exiting. Goodbye!")
        self.__run = False

