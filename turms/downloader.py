#   --- Turms ---
#   Module for handling reading data from
#   bytestring to a file.
#
#   Sipi Ylä-Nojonen, 2022

import logger as log
from pathvalidate import sanitize_file_path, validate_file_path

# TODO: Whether or not to lock the file between writing chunks

class Downloader():
    __path = None

    def __init__(self, path):
        self.assign_file(path)

    def assign_file(self, path):
        """
        Sanitize and validate a filepath for saving file
        and assign path for download.

        :param path:        Directory path to the file location.
        :return:
        """

        # Sanitize user input file path by replacing
        # unprintable characters with "". Also adds additional
        # underscore to filename if it is a system reserved name.
        san_location = sanitize_file_path(path)


        # Validate filepath to determine if sanitation was successful
        # and path is a valid filepath.

        # By default, check maximum length of path to fit platform
        # universally, fitting the smallest limit set by Windows
        # at 260 characters.
        # Also check that path doesn't contain reserved
        # names such as 'nul'.
        # Raises pathvalidate.ValidationError if validation isn't successful

        # https://github.com/thombashi/pathvalidate/blob/master/pathvalidate/_filepath.py
        validate_file_path(san_location, "universal")

        self.__path = san_location
        return


    def write_to_file(self, chunk):
        """
        Write parameter chunk to file.

        :param chunk: Chunk to be read to file.
        :return:
        """
        # If no path is specified beforehand with assign file
        # refrain from downloading to prevent overwriting other files.
        if not self.__path:
            log.warning("No filepath specified for download.")
            return
        else:
            # Open file with append mode
            with open(self.__path, "ab") as f:      # Should close file automatically in case of error.
                f.write(chunk)
                f.close()


