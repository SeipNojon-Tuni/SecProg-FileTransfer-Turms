#   --- Turms ---
#   Module for handling reading data from
#   bytestring to a file.
#
#   Sipi Ylä-Nojonen, 2022

import logging as log
from os.path import exists

# TODO: Whether or not to lock the file between writing chunks

class Downloader():
    __path = None

    def assign_file(self, path, filename):
        """
        Check that file doesn't already exist and
        if successfull assign it for downloading.

        :param path:        Directory path to the file location.
        :param filename:    Name of the file.
        :return:
        """
        if exists(path + "/" + filename):
            log.error("Filepath already exists.")
            return
        else:
            self.__path = path + "/" + filename
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


