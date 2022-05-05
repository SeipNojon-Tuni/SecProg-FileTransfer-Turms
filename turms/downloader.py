#   --- Turms ---
#   Module for handling reading data from
#   bytestring to a file.
#
#   Sipi Ylä-Nojonen, 2022
import config
import encrypt
import request_handler
from logger import TurmsLogger as Logger
from config import Config as cfg
from os.path import exists
from os import remove

from pathvalidate import sanitize_filepath, validate_filepath
import io
from cryptography.hazmat.primitives import padding

DEFAULT_DL_DIRECTORY = "./downloads"


class Downloader:
    __path = None
    __decryptor = None

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
        if exists(self.__path):
            remove(self.__path)
        return

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

    def create_decryptor(self, password, salt, iv):
        """ Create decryptor object for decrypting data.

        :param decryptor:   Decryptor object.
        :param salt:        Salt used for encryption.
        :param iv:          Initialization vector for decryption.
        """

        if not password or not salt or not iv:
            Logger.error("Missing parameters. Cannot create decryptor.")
            return

        self.__decryptor = encrypt.Decryptor(password, salt, iv)
        return

    def decrypt_and_write(self, data):
        """ Create decryptor and decrypt file content, then save it to file.

        :param data:    Data to write to file.
        """

        # File is handled here as chunks to make it possible to properly
        # unpad last chunk despite file size.
        # Even though server transfers file as chunks it has to be read
        # fully to memory before decrypting and writing it to file because
        # of how HTTP response is received as one response.
        size = len(data)
        written = 0
        f = io.BytesIO(data)
        chunk = None
        chk_size = int(cfg.get_turms_val("ChunkSize", request_handler.CHUNK_SIZE))

        if not self.__decryptor:
            Logger.warning("No decryptor instance created. Cannot decrypt data.")
            return

        while size - written > chk_size:
            # While size greater than one chunk size remains to be
            chunk = f.read(request_handler.CHUNK_SIZE)
            chunk = self.__decryptor.decrypt(chunk)
            written += len(chunk)
            self.write_to_file(chunk)
            del chunk

        # (Less than) one chunk
        chunk = f.read(size - written)
        # Save chunk size because it changes in
        # unpadding process
        chunk = self.__decryptor.decrypt(chunk)
        chunk += self.__decryptor.finalize()

        # Unpad undersized chunk for AES encryption.
        unpad = padding.PKCS7(chk_size).unpadder()
        chunk = unpad.update(chunk)
        chunk += unpad.finalize()

        self.write_to_file(chunk)
        self.__decryptor = None
        return

    def compare_checksum(self, checksum):
        """ Compares given checksum to file in path defined for this instance
        to determine if sums match.

        :param checksum:    Checksum to compare to path.
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
                return checksum == ref_sum



