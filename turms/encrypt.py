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
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class Encryptor:
    __machine = None
    __salt = None
    __iv = None
    __encryptor = None
    __decryptor = None

    def __init__(self, password):
        """ Class wrapper for encrypting data with python cryptography
        module AES. Key is generated from user input password with
        SHA256."""

        # Create encryption key based on user input password.
        # Based on cryptography module documentation and example.
        # https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
        bpass = bytes(password, "utf-8")

        self.__salt = os.urandom(16)            # According to python documentation unpredictable
                                                # enough to be suitable for cryptography.
                                                # https://docs.python.org/3/library/os.html
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.__salt,
            iterations=390000
        )
        key = kdf.derive(bpass)

        # Initialize AES cipher with generated key and iv.
        # https://cryptography.io/en/latestl/hazmat/primitives/symmetric-encryption/

        self.__iv = os.urandom(16)                                      # Like salt, use os.urandom for
                                                                        # initialization vector since it
                                                                        # is cryptosafe.

        cipher = Cipher(algorithms.AES(key), modes.CBC(self.__iv))
        self.__encryptor = cipher.encryptor()
        self.__decryptor = cipher.decryptor()                           # Encryptor can be allowed to
                                                                        # decrypt what it has generated.

        return

    def encrypt(self, content):
        """ Encrypt given content and return encrypted """

        token = self.__encryptor.update(content) + self.__encryptor.finalize()
        return token


    def decrypt(self, content):
        """ Decrypt given content and return decrypted """
        raw = self.__decryptor.update(content) + self.__decryptor.finalize()
        return raw

    def get_salt(self):
        """ Return salt used for encryption key """
        return self.__salt

    def get_iv(self):
        """ Get initialization vector """
        return self.__iv


class Decryptor:

    __salt = None
    __decryptor = None

    def __init__(self, password, salt):
        """ Class wrapper for decrypting data with python cryptography
        AES cipher. Similar to Encryptor class but separated since Decryptor
        uses predefined salt to with user input password to determine correct key,
        so it should only be used for decryption."""

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
        key = base64.urlsafe_b64encode(kdf.derive(password))

        # Initialize AES cipher with generated key and iv.
        # https://cryptography.io/en/latestl/hazmat/primitives/symmetric-encryption/

        self.__iv = os.urandom(16)                                      # Like salt, use os.urandom for
                                                                        # initialization vector since it
                                                                        # is cryptosafe.
        cipher = Cipher(algorithms.AES(key), modes.CBC(self.__iv))
        self.__decryptor = cipher.decryptor()

        return

    def decrypt(self, content):
        """ Decrypt given content and return decrypted """
        raw = self.__decryptor.update(content) + self.__decryptor.finalize()
        return raw