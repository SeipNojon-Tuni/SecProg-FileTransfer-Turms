#   --- Turms ---
#   Request handler to be delegated by server
#   to server requests from single user connection.
#
#   Sipi Ylä-Nojonen, 2022
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
        self.flush()
        self.finish()

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
        self.set_status(200)
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

class FileRequestHandler(TurmsRequestHandler):
    def head(self):
        """ Create response for 'HEAD' method request in path '/content/*.*' """
        self.ok()

    def get(self):
        """ Create response for 'GET' method request in path '/content/*.*' """
        try:
            filename = json.loads(self.request.body)

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
                        chunk = file.read()

                    try:
                        self.write(chunk)
                        self.flush()
                    except iostream.StreamClosedError:
                        logger.warning("IoStream to user %s was closed prematurely." % self.request.host_name)
                        break
                    finally:
                        del chunk
                        # Pause the coroutine so other handlers can run
                        gen.sleep(0.000000001)  # 1 nanosecond
            return

        except json.JSONDecodeError:
            self.bad_request()
        except pathvalidate.ValidationError:
            # Respond with 'Bad request' if filename is
            # malformed or not a valid filename.
            self.bad_request()

