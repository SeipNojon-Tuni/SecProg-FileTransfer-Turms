#   --- Turms ---
#   Implementation for handling and
#   providing user with download options
#   and server content information
#   server side.
#
#   Sipi Ylä-Nojonen, 2022

CONTENT_PATH = "./content"

from os import listdir, mkdir
from os.path import isfile, isdir, join, getsize, sep, abspath, exists
import json
from pathvalidate import sanitize_filename, validate_filename, ValidationError


class ServerFileHandler:

    @staticmethod
    def raw_server_content():
        """
        Get filenames in content directory

        :return:    List of filenames present
        """

        # From content directory get files and not directories.
        try:
            # Create content directory if not present
            if not exists(CONTENT_PATH):
                mkdir(CONTENT_PATH)

            if not isdir(CONTENT_PATH):
                return []


            onlyfiles = [f for f in listdir(CONTENT_PATH) if isfile(join(CONTENT_PATH, f))]
            return onlyfiles
        except FileNotFoundError:

            return []

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
                raise ValidationError("Illegal filepath.")

            # Open file for reading when path has been validated.
            if isfile(path):
                file = open(path, "rb")
                return file, getsize(path)
            else:
                # Was a directory path
                return None, None




