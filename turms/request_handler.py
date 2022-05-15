#   --- Turms ---
#   Request handler to be delegated by server
#   to server requests from single user connection.
#
#   Sipi Ylä-Nojonen, 2022

import pathvalidate
from tornado import web, iostream, gen
import tornado.httputil as tutil
import base64

import encrypt
import server

CHUNK_SIZE = 4096

from logger import TurmsLogger as Logger
from server_file_handler import ServerFileHandler as Sfh
from config import Config as Cfg


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

    def prepare(self):
        """ Log request before processing """
        Logger.warning("User requested path '%s' with %s, from %s." % (self.request.path,
                                                                       self.request.method,
                                                                       self.request.remote_ip), "turms.server")
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
        Logger.warning("Responding user %s with %s %s" %
                       (self.request.remote_ip,
                        400, tutil.responses[400]),
                       "turms.server")

        self.set_status(400, tutil.responses[400])
        self.flush()
        self.finish()

    def forbidden(self):
        """ Construct basic response with status '405 Forbidden' """
        Logger.warning("Responding user %s with %s %s" %
                       (self.request.remote_ip,
                        405, tutil.responses[405]),
                       "turms.server")

        self.set_status(405, tutil.responses[405])
        self.flush()
        self.finish()

    def not_found(self):
        """ Construct basic response with status '404 Not found' """
        Logger.warning("Responding user %s with %s %s" %
                       (self.request.remote_ip,
                        404, tutil.responses[404]),
                       "turms.server")

        self.set_status(404, tutil.responses[404])
        self.flush()
        self.finish()

    def ok(self):
        """ Construct basic response with status '200 OK' """
        Logger.warning("Responding user %s with %s %s" %
                       (self.request.remote_ip,
                        200, tutil.responses[200]),
                       "turms.server")

        self.set_status(200, tutil.responses[200])

    def internal_server_error(self):
        Logger.warning("Responding user %s with %s %s" %
                       (self.request.remote_ip,
                        500, tutil.responses[500]),
                       "turms.server")

        self.set_status(500, tutil.responses[500])
        self.flush()
        self.finish()

    def data_received(self, chunk: bytes):
        """ Streamed requests not supported """
        self.bad_request()


# ---------------------------------------------------
# Path specific request handlers for different request paths
# eg.   --> IndexRequestHandler for "/"
#       --> DirectoryRequestHandler for "/dir/"
#       --> FileRequestHandler for "/download/*"
class IndexRequestHandler(TurmsRequestHandler):

    def head(self):
        """ Create response for 'HEAD' method request for path '/' """
        self.set_cookie("_xsrf", self.xsrf_token)
        self.ok()

    def get(self):
        """ Create response for 'GET' method request for path '/' """

        # Add generated xsrf-token to response for
        # use later. (Unnecessary since no other than
        # GET and HEAD methods are allowed.)
        self.set_cookie("_xsrf", self.xsrf_token)

        self.ok()
        self.write("")
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
        files = Sfh.fetch_server_content()
        self.write(files)

        self.flush()
        self.finish()


class FileRequestHandler(TurmsRequestHandler):

    __encryptor = None
    __allow_unencrypted = False

    # Application should be Turms web application instead of
    # tornado.web.Application super class object
    application: server.TurmsApp

    def prepare(self):
        """ Prepare before handling request. Create encryption device where necessary. """
        self.__allow_unencrypted = Cfg.get_bool("TURMS", "AllowUnencrypted", False)

        # Create encryptor for this user request.
        # If unencrypted transfer is not allowed and no password is defined raises ValueError.
        try:
            self.__encryptor = self.application.get_encryptor()
            return
        except ValueError as e:
            self.internal_server_error()
            Logger.error(e, "turms.server")
            return

    def head(self):
        """ Create response for 'HEAD' method request in path '/download/*.*' """
        try:
            # Split to: "" ,  "download", [path to file]
            # If <path to file> is not file name refuse download since we only serve files
            # inside the root content directory. List should only have one item, the filename.
            splitpath = self.request.path.split("/")
            splitpath.pop(0)    # Empty string created by split before leading dash
            splitpath.pop(0)    # "download"
            if len(splitpath) > 1:
                self.bad_request()
                return

            # File name could be fetched as the last part of url directly without
            # above checks but since we want to return error for malformed request if path
            # is not filename instead of "404, page not found"
            filename = splitpath[-1]

            # ServerFileHandler does sanitation and filename validation internally.
            # Raises pathvalidate.ValidationError if validation fails.
            file, size = Sfh.get_file_object(filename)

            if file is None:
                self.not_found()
                return
            else:
                checksum = encrypt.get_checksum(file.read())

                # Not needed after this in HEAD response.
                file.close()

                # Set encryption headers
                if self.__allow_unencrypted and not self.__encryptor:
                    self.add_header("encrypted", "False")
                else:
                    self.add_header("encrypted", "True")

                # No point in returning salt and initialization vector
                # in HEAD response when they change for each response.
                self.add_header("salt", base64.urlsafe_b64encode(self.__encryptor.get_salt()))
                self.add_header("iv", base64.urlsafe_b64encode(self.__encryptor.get_salt()))
                self.add_header("checksum", base64.urlsafe_b64encode(checksum))
                self.ok()
                self.finish()

        except pathvalidate.ValidationError:
            # Respond with 'Bad request' if filename is
            # malformed or not a valid filename.
            self.bad_request()

    def get(self):
        """ Create response for 'GET' method request in path '/download/*.*' """
        try:
            # Split to: "" ,  "download", [path to file]
            # If <path to file> is not file name refuse download since we only serve files
            # inside the root content directory. List should only have one item, the filename.
            splitpath = self.request.path.split("/")
            splitpath.pop(0)    # Empty string created by split before leading dash
            splitpath.pop(0)    # "download"
            if len(splitpath) > 1:
                self.bad_request()
                return

            # File name could be fetched as the last part of url directly without
            # above checks but since we want to return error for malformed request if path
            # is not filename instead of "404, page not found"
            filename = splitpath[-1]

            # ServerFileHandler does sanitation and filename validation internally.
            # Raises pathvalidate.ValidationError if validation fails.
            file, size = Sfh.get_file_object(filename)

            if file is None:
                self.not_found()
                return
            else:
                # Read from file to response body in chunks until completed.
                read = 0
                checksum = encrypt.get_checksum(file.read())
                file.seek(0, 0)

                if self.__allow_unencrypted and not self.__encryptor:
                    self.add_header("encrypted", "False")
                else:
                    self.add_header("encrypted", "True")

                self.add_header("salt", base64.urlsafe_b64encode(self.__encryptor.get_salt()))
                self.add_header("iv", base64.urlsafe_b64encode(self.__encryptor.get_iv()))
                self.add_header("checksum", base64.urlsafe_b64encode(checksum))
                self.add_header("filesize", str(size))
                self.ok()
                self.flush()

                # Data remains to be read
                while size - read > 0:
                    # While size greater than one chunk size remains to be
                    if size - read > CHUNK_SIZE:
                        chunk = file.read(CHUNK_SIZE)
                        read += len(chunk)

                    # Less than one chunk
                    else:
                        chunk = file.read(size - read)
                        read += len(chunk)
                    try:
                        # There should be encryptor when encryption is required.
                        if not self.__encryptor and not self.__allow_unencrypted:
                            Logger.error("Server", "turms.server")
                            self.internal_server_error()

                        # Each chunk will be sent to client on flush.
                        if self.__allow_unencrypted:
                            final = chunk
                        else:
                            final = self.__encryptor.encrypt(chunk)
                            if size == read:
                                final += self.__encryptor.finalize()
                        self.write(final)
                        self.flush()
                    except iostream.StreamClosedError as e:
                        Logger.warning(e, "turms.server")
                        break
                    finally:
                        del chunk
                        # Sleep to not block and to let other tasks run
                        gen.sleep(0.000001)
                self.finish()
                file.close()
                return

        except pathvalidate.ValidationError:
            # Respond with 'Bad request' if filename is
            # malformed or not a valid filename.
            self.bad_request()
