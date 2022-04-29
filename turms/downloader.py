#   --- Turms ---
#   Module for handling reading data from
#   bytestring to a file.
#
#   Sipi Ylä-Nojonen, 2022
import encrypt
import request_handler
from logger import TurmsLogger as Logger
from pathvalidate import sanitize_filepath, validate_filepath, Platform
import io

# TODO: Whether or not to lock the file between writing chunks

DEFAULT_DL_DIRECTORY = "./downloads"


class Downloader:
    __path = None

    def __init__(self, path):
        self.assign_file(path)

    def assign_file(self, path):
        """
        Sanitize and validate a filepath for saving file
        and assign path for download.

        :param path:    Directory path to the file location.
        :return:
        """
        # TODO: ADD deleting original file if present to overwrite it.

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

    def decrypt_and_write(self, data, password, salt, iv):
        """ Create decryptor and decrypt file content, then save it to file.

        :param data:       Data to write to file.
        :param password:    User supplied password.
        :param salt:        Salt used for encryption.
        :param iv:          Initialization vector for decryption.
        """
        decryptor = encrypt.Decryptor(password, salt, iv)

        # TODO: REMOVE
        print(data)
        size = len(data)
        written = 0
        f = io.BytesIO(data)
        chunk = None

        while size - written > 0:
            # While size greater than one chunk size remains to be
            if size - written > request_handler.CHUNK_SIZE:
                chunk = f.read(request_handler.CHUNK_SIZE)
                chunk = decryptor.decrypt(chunk)
                written += request_handler.CHUNK_SIZE

            # Less than one chunk
            else:
                chunk = f.read(size - written)
                chunk = decryptor.decrypt(chunk)

                # Pad undersized chunk for AES encryption.
                # chunk = decryptor.unpad(chunk, size - written)
                written += len(chunk)

        # TODO: REMOVE
        print(chunk)
        self.write_to_file(chunk)
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
                ref_sum = encrypt.get_checksum(f)
                return checksum == ref_sum



