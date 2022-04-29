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
from cryptography.hazmat.primitives import padding

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
    __decryptor = None

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

        # Encryptor can be allowed to
        # decrypt what it has generated.
        self.__decryptor = cipher.decryptor()
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

    @staticmethod
    def pad(data, size):
        """ Pad data to predetermined size.

        :param data:    Data to be padded.
        :param size:    Size of the block after padding.
        """

        # Based on padding module documentation tutorial.
        # https://cryptography.io/en/latest/hazmat/primitives/padding/
        padder = padding.PKCS7(size).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data


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
        raw = self.__decryptor.update(content) + self.__decryptor.finalize()
        return raw

    @staticmethod
    def unpad(pad_data, size):
        """ Unpad data to from predetermined size.

        :param pad_data:   Padded data
        :param size:       Size of the padded block.
        """

        # Based on padding module documentation tutorial.
        # https://cryptography.io/en/latest/hazmat/primitives/padding/
        unpadder = padding.PKCS7(size).unpadder()
        padded_data = unpadder.update(pad_data) + unpadder.finalize()
        return padded_data


class KeyGen:
    """ Generate server key pair and certificate with """
    pass