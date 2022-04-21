#   --- Turms ---
#   Request handler to be delegated by server
#   to server requests from single user connection.
#
#   Sipi Ylä-Nojonen, 2022
import logging

import pathvalidate
from tornado import web, iostream, gen
import tornado.httputil as tutil
from pathvalidate import validate_filename, sanitize_filename
import json

import logger
import server_file_handler as sfh

CHUNK_SIZE = 2048

class TurmsRequestHandler(web.RequestHandler):
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
    __logger = "turms.req_handler"

    def set_default_headers(self):
        pass

    # Unsupported methods
    def post(self):
        """ Default response for method 'POST' - not allowed """
        self.forbidden()

    def options(self):
        """ Default response for method 'OPTIONS' - not allowed """
        self.forbidden()

    def delete(self):
        """ Default response for method 'DELETE' - not allowed """
        self.forbidden()

    def put(self):
        """ Default response for method 'PUT' - not allowed """
        self.forbidden()

    def patch(self):
        """ Default response for method 'PATCH' - not allowed """
        self.forbidden()


    def bad_request(self):
        """ Construct basic response with status '400 Bad request' """
        self.set_status(400, tutil.responses[400])
        self.flush()
        self.finish()

    def forbidden(self):
        """ Construct basic response with status '405 Forbidden' """
        self.set_status(405, tutil.responses[405])
        self.flush()
        self.finish()

    def not_found(self):
        """ Construct basic response with status '404 Not found' """
        self.set_status(404, tutil.responses[404])
        self.flush()
        self.finish()

    def ok(self):
        """ Construct basic response with status '200 OK' """
        self.set_status(200, tutil.responses[200])

# ---------------------------------------------------
# Path specific request handlers for different request paths
# eg.   --> IndexRequestHandler for "/"
#       --> DirectoryRequestHandler for "/dir/"


class IndexRequestHandler(TurmsRequestHandler):

    def head(self):
        """ Create response for 'HEAD' method request for path '/' """
        self.ok()

    def get(self):
        """ Create response for 'GET' method request for path '/' """
        self.set_cookie("_xsrf", self.xsrf_token)
        self.ok()
        self.write("The index.")
        self.flush()
        self.finish()


class DirectoryRequestHandler(TurmsRequestHandler):

    def head(self):
        """ Create response for 'HEAD' method request in path '/dir/' """
        self.ok()

    def get(self):
        """ Create response for 'GET' method request in path '/dir/' """

        self.set_status(200)
        # Write list of available files for download as json object
        files = sfh.fetch_server_content()
        self.write(files)
        pass

        self.flush()
        self.finish()

    def post(self):
        self.not_found()


class FileRequestHandler(TurmsRequestHandler):
    def head(self):
        """ Create response for 'HEAD' method request in path '/download/*.*' """
        self.ok()

    def get(self):
        """ Create response for 'GET' method request in path '/download/*.*' """
        try:
            # File name should be the last part of the url.
            filename = self.request.path.split("/")[-1]

            # logger.info_server("User %s requested %s " % (self.request.host_name, filename))

            # ServerFileHandler does sanitation and filename validation internally.
            # Raises pathvalidate.ValidationError if validation fails.
            file = sfh.get_file_object(filename)

            # User requested file is not available on server
            if file is None:
                self.not_found()
                return
            else:
                # Read from file to response body in chunks until completed.
                file.seek(0, 2)
                size = file.tell()
                file.seek(0, 0)
                read = 0

                # Data remains to be read
                while size - read > 0:
                    # While size greater than one chunk size remains to be
                    if size - read > CHUNK_SIZE:
                        chunk = file.read(CHUNK_SIZE)
                        read += CHUNK_SIZE

                    # Less than one chunk
                    else:
                        chunk = file.read(size-read)
                        read += len(chunk)
                    try:
                        # Each chunk will be sent to client on flush
                        self.ok()
                        self.write(chunk)
                        self.flush()
                    except iostream.StreamClosedError:
                        break
                    finally:
                        del chunk
                        # Pause the coroutine so other handlers can run
                        gen.sleep(0.000000001)  # 1 nanosecond
                self.finish()
                file.close()
                return

        except pathvalidate.ValidationError:
            # Respond with 'Bad request' if filename is
            # malformed or not a valid filename.
            self.bad_request()

