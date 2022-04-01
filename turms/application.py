#   --- Turms ---
#   Application framework implementation
#
#   Sipi Ylä-Nojonen, 2022

import pyglet
import controller as ctrl

class App():

    __window = None
    __controller = None

    def __init__(self):
        return

    def run(self):
        """
        Run through app initialization actions
        such as creating window and controllers for
        application.
        """

        # Create pyglet window for app and
        # controller object for input handling.
        self.__window = self.create_window()
        self.__controller = ctrl.Controller(self.__window)

        # App 'mainloop'
        pyglet.app.run()


    def create_window(app):
        """
        Create pyglet window to serve as
        GUI for the application and setup
        elements for the window.

        :param app : Application to link window to.
        :return: Created pyglet window.
        """

        window = pyglet.window.Window(1280, 720, "Turms File Transfer", resizable=True)
        window.set_minimum_size(640, 400)



        @window.event
        def on_draw():
            window.clear()

        return window

