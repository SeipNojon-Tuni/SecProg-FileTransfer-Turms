#   --- Turms ---
#   Request handler to be delegated by server
#   to server requests from single user connection.
#
#   Sipi Ylä-Nojonen, 2022

import tornado.web


class TurmsRequestHandler(tornado.web.RequestHandler):
    """
    Implementation of tornado.web's RequestHandler class
    responsible for handling and writing responses
     for single client connection.
    """

    # No need to support other methods than GET and HEAD
    # so prevent any unauthorized modification of server
    # content by not accepting any other methods.
    SUPPORTED_METHODS = ("GET", "HEAD")

    async def prepare(self):
        pass

    def head(self):
        pass

    def get(self):
        self.write("Nothing to show here.")

    # Unsupported methods
    def post(self):
        pass

    def options(self):
        pass

    def delete(self):
        pass

    def put(self):
        pass

    def patch(self):
        pass