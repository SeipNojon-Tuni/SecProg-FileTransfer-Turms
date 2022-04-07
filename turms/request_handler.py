#   --- Turms ---
#   Request handler to be delegated by server
#   to server requests from single user connection.
#
#   Sipi Ylä-Nojonen, 2022

import tornado.web
import logger


class TurmsRequestHandler(tornado.web.RequestHandler):
    """
    Implementation of tornado.web's RequestHandler class
    responsible for handling and writing responses
    for single client connection.
    This subclass specifies server wide behaviour in responses.
    Path specific implementations should be derived from this.
    """

    # No need to support other methods than GET and HEAD
    # so prevent any unauthorized modification of server
    # content by not accepting any other methods.
    SUPPORTED_METHODS = ("GET", "HEAD")

    def set_default_headers(self):
        

    # Unsupported methods
    def post(self):
        self.set_status(405)
        self.flush()
        self.finish()

    def options(self):
        self.set_status(405)
        self.flush()
        pass

    def delete(self):
        self.set_status(405)
        self.flush()
        self.finish()

    def put(self):
        self.set_status(405)
        self.flush()
        self.finish()

    def patch(self):
        self.set_status(405)
        self.flush()
        self.finish()

class DirectoryRequestHandler(TurmsRequestHandler):

    def head(self):
        self.set_status(200)
        self.flush()
        self.finish()

    def get(self):
        self.set_status(200)
        self.write("Nothing to show here.")
        self.flush()
        self.finish()
