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

def get_checksum(file):
    """ Get checksum for file to determine if it has been modified or corrupted. """
    digest = hashes.Hash(hashes.SHA256())
    digest.update(file)
    cs = digest.finalize()
    return cs


class Encryptor:
    __machine = None
    __salt = None
    __iv = None
    __encryptor = None

    def __init__(self, password):
        """ Class wrapper for encrypting data with python cryptography
        module AES. Key is generated from user input password with
        SHA256."""

        # Create encryption key based on user input password.
        # Based on cryptography module documentation and example.
        # https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
        bpass = bytes(password, "utf-8")

        # According to python documentation unpredictable
        # enough to be suitable for cryptography.
        # https://docs.python.org/3/library/os.html
        self.__salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.__salt,
            iterations=390000
        )
        key = kdf.derive(bpass)

        # Initialize AES cipher with generated key and iv.
        # https://cryptography.io/en/latestl/hazmat/primitives/symmetric-encryption/

        # Like salt, use os.urandom for
        # initialization vector since it
        # is cryptosafe.
        self.__iv = os.urandom(16)

        cipher = Cipher(algorithms.AES(key), modes.CBC(self.__iv))
        self.__encryptor = cipher.encryptor()
        return

    def encrypt(self, content):
        """ Encrypt given content and return encrypted """
        return self.__encryptor.update(content)

    def finalize(self):
        """ Finalize encryption """
        return self.__encryptor.finalize()

    def get_salt(self):
        """ Return salt used for encryption key """
        return self.__salt

    def get_iv(self):
        """ Get initialization vector """
        return self.__iv

    def get_tag(self):
        """ Get authentication tag """
        return self.__encryptor.tag

class Decryptor:

    __decryptor = None
    __salt = None
    __iv = None

    def __init__(self, password, salt, iv):
        """ Class wrapper for decrypting data with python cryptography
        AES cipher. Similar to Encryptor class but separated since Decryptor
        uses predefined salt to with user input password to determine correct key,
        so it should only be used for decryption.

        :param password:   Password to use for key derivation.
        :param salt:       Salt supplied by encryptor.
        :param iv:         Initialization vector supplied by encryptor.
        """

        # Create encryption key based on user input password.
        # Based on cryptography module documentation and example.
        # https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
        bpass = bytes(password, "utf-8")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        key = kdf.derive(bpass)

        # Initialize AES cipher with generated key and iv.
        # https://cryptography.io/en/latestl/hazmat/primitives/symmetric-encryption/

        # Decryptor uses initialization vector provided by user.
        # Don't allow to be used for encryption.
        self.__iv = iv

        cipher = Cipher(algorithms.AES(key), modes.CBC(self.__iv))
        self.__decryptor = cipher.decryptor()
        return

    def decrypt(self, content):
        """ Decrypt given content and return decrypted """
        return self.__decryptor.update(content)

    def finalize(self):
        """ Finalize decryptor context """
        return self.__decryptor.finalize()


class KeyGen:
    """ Generate server key pair and certificate with """
    pass