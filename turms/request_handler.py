#   --- Turms ---
#   Request handler to be delegated by server
#   to server requests from single user connection.
#
#   Sipi Ylä-Nojonen, 2022

import tornado.web
import logger
import server_file_handler as sfh


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
        pass

    # Unsupported methods
    def post(self):
        self.set_status(405)
        self.flush()
        self.finish()

    def options(self):
        self.set_status(405)
        self.flush()
        self.finish()

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

# ---------------------------------------------------
# Path specific request handlers for different request paths
# eg.   --> IndexRequestHandler for "/"
#       --> DirectoryRequestHandler for "/dir/"

class IndexRequestHandler(TurmsRequestHandler):

    def head(self):
        self.set_status(200)
        self.flush()
        self.finish()

    def get(self):
        self.set_status(200)
        self.write("The index.")
        self.flush()
        self.finish()

class DirectoryRequestHandler(TurmsRequestHandler):

    def head(self):
        self.set_status(200)
        self.flush()
        self.finish()

    def get(self):
        self.set_status(200)
        # Write list of available files for download as json object
        files = sfh.fetch_server_content()
        self.write(files)
        pass

        self.flush()
        self.finish()
