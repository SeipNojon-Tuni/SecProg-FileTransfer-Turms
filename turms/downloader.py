#   --- Turms ---
#   Module for handling reading data from
#   bytestring to a file.
#
#   Sipi Ylä-Nojonen, 2022


DEFAULT_DL_DIRECTORY = "./downloads"

from request_handler import CHUNK_SIZE
from logger import TurmsLogger as Logger
from config import Config as cfg
from os.path import exists
from os import remove, mkdir

import encrypt
from pathvalidate import sanitize_filepath, validate_filepath


class Downloader:
    __path = None
    __decryptor = None
    __filesize = 0
    __written = 0
    __checksum = None

    # For mitigating unnecessary
    # progress prints
    __count = 0

    # Collect decryptor parameters from
    # headers as they are received to
    # initialize decryptor
    __decryptor_params = {"password": None,
                          "salt": None,
                          "iv": None}

    def __init__(self, path):
        self.assign_file(path)

    def assign_file(self, path):
        """
        Sanitize and validate a filepath for saving file
        and assign path for download.

        :param path:    Directory path to the file location.
        :return:
        """

        # Sanitize user input file path by replacing
        # unprintable characters with "". Also adds additional
        # underscore to filename if it is a system reserved name.
        san_location = sanitize_filepath(path, "", "auto")

        # Validate filepath to determine if sanitation was successful
        # and path is a valid filepath.

        # By default, check maximum length of path to fit platform.
        # Also check that path doesn't contain platform specific reserved
        # names such as 'nul'.
        # Raises pathvalidate.ValidationError if validation isn't successful

        # https://github.com/thombashi/pathvalidate/blob/master/pathvalidate/_filepath.py
        validate_filepath(san_location, "auto")
        self.__path = san_location

        # Delete original file at location if it exists. Done before starting
        # download so that writing can open file in append mode and doesn't have
        # to differentiate between downloaded chunks and existing file.
        if self.file_exists():
            remove(self.__path)
        return

    def file_exists(self):
        """ Does assigned path exist? Can be used to check if download was completed or
        if there is a file of such name before downloading.
        """
        return exists(self.__path)

    def write_to_file(self, chunk):
        """
        Write parameter chunk to file.

        :param chunk: Chunk to be read to file.
        :return:
        """
        # If no path is specified beforehand with assign file
        # refrain from downloading.
        if not self.__path:
            Logger.warning("No filepath specified for download.")
            return
        else:
            # Should close file automatically in case of error.
            with open(self.__path, "ab") as f:
                f.write(chunk)
                f.close()

    def create_decryptor(self):
        """ Create decryptor object for decrypting data based on set parameters."""

        password = self.__decryptor_params["password"]
        salt = self.__decryptor_params["salt"]
        iv = self.__decryptor_params["iv"]

        if not password or not salt or not iv:
            Logger.error("Missing parameters. Cannot create decryptor.")
            return
        self.__decryptor = encrypt.Decryptor(password, salt, iv)

        # Not needed after decryptor is created
        self.__decryptor_params = {}
        return

    def set_filesize(self, size: int):
        """ Set expected file size for downloaded content. """
        self.__filesize = int(size)

        # Initialize already received data here too
        self.__written = 0
        self.__count = 0
        return

    def set_checksum(self, chksum: bytes):
        """ Set server given checksum that should match downloaded file. """
        self.__checksum = chksum
        return

    def decrypt_param(self, key, value):
        """ Set up parameters for creating decryptor. """
        self.__decryptor_params[key] = value

    def decryptor_ready(self):
        """ Whether this downloader has decryptor set up."""
        if self.__decryptor:
            return True
        else:
            return False

    def chunk_decrypt_and_write(self, data):
        """ Decrypt and write single chunk of data from received response body.
        Should be used for streaming callback function for tornado.httpclient.HTTPRequest."""

        chunk = data
        chk_size = int(cfg.get_turms_val("ChunkSize", CHUNK_SIZE))
        self.__count += 1

        if not self.__decryptor:
            raise ValueError("No decryptor instance created. Cannot decrypt data.")

        if self.__filesize - self.__written > chk_size:
            # While size greater than one chunk size remains to be
            chunk = self.__decryptor.decrypt(chunk)
            self.__written += len(chunk)
            self.write_to_file(chunk)
            del chunk

            # Progress bar with every 20th chunk
            if self.__count == 1 or self.__count % 20 == 0:
                self.progress()
            return

        # (Less than or) one chunk
        else:
            # Decrypt
            chunk = self.__decryptor.decrypt(chunk)
            chunk += self.__decryptor.finalize()

            self.__written += len(chunk)
            self.write_to_file(chunk)
            del chunk

            # Progress bar with last chunk.
            self.progress()



    def compare_checksum(self):
        """ Compares given checksum to file in path defined for this instance
        to determine if sums match.

        :return:            Whether checksums match.
        """
        # If no path is specified there shouldn't be anything
        # to compare to.
        if not self.__path:
            Logger.warning("No filepath specified for download.")
            return False
        else:
            # Should close file automatically in case of error.
            with open(self.__path, "rb") as f:
                ref_sum = encrypt.get_checksum(f.read())
                return self.__checksum == ref_sum

    def remove_file(self):
        """ Remove assigned file """
        if exists(self.__path):
            remove(self.__path)
        return

    def progress(self):
        """ Print out progress bar """

        perc = self.__written / self.__filesize * 100
        bar = "Progress %0.2f%s" % (perc, "%")
        Logger.info(bar)

    @staticmethod
    def create_default_dir():
        """ Create default download directory if it doesn't exist"""

        if not exists(DEFAULT_DL_DIRECTORY):
            mkdir(DEFAULT_DL_DIRECTORY)
        return
