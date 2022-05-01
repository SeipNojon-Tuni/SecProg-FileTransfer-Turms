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
import base64
from cryptography.hazmat.primitives import padding


import encrypt
from logger import TurmsLogger as Logger
from server_file_handler import ServerFileHandler as Sfh
from config import Config as cfg

CHUNK_SIZE = 1024


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
                                                                       self.request.remote_ip), "tornado.access")

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

    def internal_server_error(self):
        self.set_status(500, tutil.responses[500])
        self.flush()
        self.finish()


# ---------------------------------------------------
# Path specific request handlers for different request paths
# eg.   --> IndexRequestHandler for "/"
#       --> DirectoryRequestHandler for "/dir/"
#       --> FileRequestHandler for "/download/*"
class IndexRequestHandler(TurmsRequestHandler):

    def head(self):
        """ Create response for 'HEAD' method request for path '/' """
        self.ok()

    def get(self):
        """ Create response for 'GET' method request for path '/' """

        # Add generated xsrf-token to response for
        # use later. (Unnecessary since no other than
        # GET and HEAD methods are allowed.)
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
        files = Sfh.fetch_server_content()
        self.write(files)

        self.flush()
        self.finish()


class FileRequestHandler(TurmsRequestHandler):

    __encryptor = None
    __allow_unencrypted = False

    def prepare(self):
        """ Prepare before handling request. Create encryption device where necessary. """
        self.__allow_unencrypted = cfg.get_bool("SERVER", "AllowUnencrypted")

        # If not allowing unencrypted transfers and no password is defined raise ValueError.
        # In case unencrypted data is allowed don't create encryptor object.

        if self.__allow_unencrypted:
            self.__encryptor = None
            return
        elif not self.__allow_unencrypted and cfg.get_server_val("Password", "") != "":
            # Create encryptor for this user request.
            self.__encryptor = encrypt.Encryptor(cfg.get_server_val("Password", ""))
            return
        else:
            self.internal_server_error()
            Logger.error("Password must be defined when unencrypted file transfer is not allowed.", "tornado.access")
            return

    def head(self):
        """ Create response for 'HEAD' method request in path '/download/*.*' """
        self.ok()

    def get(self):
        """ Create response for 'GET' method request in path '/download/*.*' """
        try:
            # File name should be the last part of the url.
            filename = self.request.path.split("/")[-1]

            # ServerFileHandler does sanitation and filename validation internally.
            # Raises pathvalidate.ValidationError if validation fails.
            file, size = Sfh.get_file_object(filename)

            # User requested file is not available on server
            if file is None:
                self.not_found()
                return
            else:
                # Read from file to response body in chunks until completed.
                read = 0
                checksum = encrypt.get_checksum(file.read())
                file.seek(0, 0)

                # Set encryption headers
                if self.__allow_unencrypted and not self.__encryptor:
                    self.add_header("encrypted", "False")
                else:
                    self.add_header("encrypted", "True")

                self.add_header("salt", base64.urlsafe_b64encode(self.__encryptor.get_salt()))
                self.add_header("iv", base64.urlsafe_b64encode(self.__encryptor.get_iv()))
                self.add_header("checksum", base64.urlsafe_b64encode(checksum))

                # Data remains to be read
                while size - read > 0:
                    # While size greater than one chunk size remains to be
                    if size - read > CHUNK_SIZE:
                        chunk = file.read(CHUNK_SIZE)
                        read += len(chunk)

                    # Less than one chunk
                    else:
                        chunk = file.read(size - read)

                        # Save chunk size because it changes in
                        # padding process
                        rsize = len(chunk)

                        # Pad undersized chunk for AES encryption.
                        # Based on padding module documentation tutorial.
                        # https://cryptography.io/en/latest/hazmat/primitives/padding/
                        chk_size = int(cfg.get_server_val("ChunkSize", CHUNK_SIZE))
                        pad = padding.PKCS7(chk_size).padder()
                        chunk = pad.update(chunk) + pad.finalize()
                        read += rsize
                    try:
                        Logger.info("%s" % str(size-read))
                        # Each chunk will be sent to client on flush.
                        if self.__allow_unencrypted:
                            final = chunk
                        else:
                            final = self.__encryptor.encrypt(chunk)
                            if size == read:
                                print("FINALIZED")
                                final += self.__encryptor.finalize()
                        self.ok()
                        self.write(final)
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

