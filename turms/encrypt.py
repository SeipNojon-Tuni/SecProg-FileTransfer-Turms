#   --- Turms ---
#   encryption module for application
#   using Python's cryptography library
#
#   Sipi Ylä-Nojonen, 2022

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encryptor:
    __machine = None
    __salt = None

    def __init__(self, password):
        """ Encrypt data with Fernet based encryption.
        Key is generated from user input password with
        SHA256."""

        # Create encryption key based on user input password.
        # Based on cryptography module documentation and example.
        # https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
        bpass = b"%s" % password

        __salt = os.urandom(16)             # According to python documentation unpredictable
                                            # enough to be suitable for cryptography.
                                            # https://docs.python.org/3/library/os.html
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=__salt,
            iterations=390000
        )

        return

    def encrypt(self, content):
        """ Encrypt given content and return encrypted """

        encrypted = None
        return encrypted

    def decrypt(self, content):
        """ Decrypt given content and return decrypted """
        decrypted = None
        return decrypted

    def get_salt(self):
        """ Return salt used for encryption key """
        return self.__salt


class Decryptor:

    __salt = None

    def __init__(self, password, salt):
        """ Object for decrypting encrypted data with Fernet
        based encryption. Separate class from the one used for
        Encryption to prevent reusing salt for encryption. """

        # Create encryption key based on user input password.
        # Based on cryptography module documentation and example.
        # https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
        bpass = b"%s" % password

        __salt = salt                       # According to python documentation unpredictable
                                            # enough to be suitable for cryptography.
                                            # https://docs.python.org/3/library/os.html
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=__salt,
            iterations=390000,
        )

        return

    def decrypt(self, content):
        """ Decrypt given content and return decrypted """
        decrypted = None
        return decrypted