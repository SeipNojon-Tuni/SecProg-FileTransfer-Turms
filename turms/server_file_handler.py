#   --- Turms ---
#   Implementation for handling and
#   providing user with download options
#   and server content information
#   server side.
#
#   Sipi Ylä-Nojonen, 2022

from os import listdir
from os.path import isfile, join, getsize, sep, abspath
import json

import pathvalidate
from pathvalidate import sanitize_filename, validate_filename

from logger import TurmsLogger as Logger

CONTENT_PATH = "./content"


class ServerFileHandler:

    @staticmethod
    def raw_server_content():
        # From content directory get files and not directories.
        onlyfiles = [f for f in listdir(CONTENT_PATH) if isfile(join(CONTENT_PATH, f))]
        return onlyfiles

    @staticmethod
    def fetch_server_content():
        # From content directory get files and not directories.
        onlyfiles = ServerFileHandler.raw_server_content()

        jsonStr = json.dumps(onlyfiles)
        return jsonStr

    @staticmethod
    def get_file_object(filename):
        """ Sanitize passed filename and try to find server
        content that corresponds to requested file. """

        # Sanitize file name and remove any illegal
        # characters to prevent f.e. directory traversal.
        san_name = sanitize_filename(filename)

        # Validate filename
        validate_filename(san_name)

        # Open file to be read as bytes for server send to user
        if not san_name in ServerFileHandler.raw_server_content():
            return None, None
        else:
            absolute_path = abspath(CONTENT_PATH) + sep
            path = absolute_path + san_name
            absolute_filepath = abspath(path)

            # Check that file location is within given directory path
            # and the path has not been traversed.
            if not absolute_filepath.startswith(absolute_path):
                raise pathvalidate.ValidationError("Illegal filepath.")

            # Open file for reading when path has been validated.
            if isfile(path):
                file = open(path, "rb")
                return file, getsize(path)
            else:
                # Was a directory path
                return None, None




