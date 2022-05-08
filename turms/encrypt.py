#   --- Turms ---
#   encryption module for application
#   using Python's cryptography library
#
#   Sipi Ylä-Nojonen, 2022

from os import urandom, path, mkdir
import datetime
import ssl

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID

from config import Config as cfg

def get_checksum(bts):
    """ Get SHA256 hash for bytestring object. """
    digest = hashes.Hash(hashes.SHA256())
    digest.update(bts)
    cs = digest.finalize()
    return cs


class KeyHolder:
    # No get method to not expose this outside through calls
    __pass = None

    def __init__(self, password):
        # Unencrypted file transfer not allowed but is attempted
        if not cfg.get_bool("TURMS", "AllowUnencrypted") and len(password) == 0:
            raise ValueError("Unencrypted file transfer is not allowed, but no password is defined.")

        """ Class to hold user password and create new encryption devices derived from it """
        self.__pass = bytes(password, "utf-8")

    def create_encryptor(self):
        """ Create new Encryptor with password """

        # Unencrypted file transfer not allowed but is attempted
        if not cfg.get_bool("TURMS", "AllowUnencrypted") and (len(self.__pass) == 0):
            raise ValueError("Unencrypted file transfer is not allowed, but no password is defined.")
        return Encryptor(self.__pass)


class Encryptor:
    __machine = None
    __salt = None
    __iv = None
    __encryptor = None

    def __init__(self, bpass):
        """ Class wrapper for encrypting data with python cryptography
        module AES. Key is generated from user input password with
        SHA256.

        :param bpass:   Password bytes to derive key from.
        """
        # Create encryption key based on user input password.
        # Based on cryptography module documentation and example.
        # https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet

        # According to python documentation unpredictable
        # enough to be suitable for cryptography.
        # https://docs.python.org/3/library/os.html
        self.__salt = urandom(32)
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
        self.__iv = urandom(16)

        cipher = Cipher(algorithms.AES(key), modes.CBC(self.__iv))
        self.__encryptor = cipher.encryptor()

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

    @staticmethod
    def get_context(password):
        """ Load up certificate and keys for us e

        :param password: Password to use for decrypting key
        """
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.check_hostname = False

        # Won't require verification from clients.
        ctx.verify_mode = ssl.CERT_OPTIONAL

        save_path = cfg.get_turms_val("CertPath", "./keys")

        ctx.load_cert_chain(
            certfile = path.join(save_path, "certificate.pem"),
            keyfile = path.join(save_path, "key.pem"),
            password = password
        )
        return ctx

    @staticmethod
    def generate_cert_chain():
        """ Generate key pair and certificate to use for HTTPS connection.

        :return: Password to use for encrypting key on disc.
        """

        save_path = cfg.get_turms_val("CertPath", "./keys")
        save_path = path.abspath(save_path)
        key_path = path.join(save_path, "key.pem")
        password = urandom(32)

        # Create key directory if not existent
        if not path.exists(save_path):
            mkdir(save_path)

        # Selfsigned certificate using cryptography libraries
        # https://cryptography.io/en/latest/x509/tutorial/
        # Generate key pair
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        with open(key_path, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(password)
            ))

        # Fetch information to include in certificate
        certdata = cfg.get_organization_info()
        KeyGen.gen_cert(key, certdata, save_path)
        return password

    @staticmethod
    def gen_cert(keypair, certdata, save_path):
        """ Create X509 certificate with parameter key and data about
        organization issuing and using this self-signed certificate.

        :param keypair:     Key pair to sign and pair with certificate
        :param certdata:    Organization data to include to certificate
        :param path:        Path to save certificate
        """

        # For a self-signed certificate the subject and issuer are always the same.
        # Name data for server entity is supplied by user. Since it is self-signed
        # connecting user has to themselves choose to trust it.

        subject = None

        # Construct X509 certificate with parameter key
        # https://cryptography.io/en/latest/x509/tutorial/
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"%s" % certdata["COUNTRY_NAME"]),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"%s" % certdata["PROVINCE_NAME"]),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"%s"  % certdata["LOCALE_NAME"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"%s" % certdata["ORGANIZATION_NAME"]),
            x509.NameAttribute(NameOID.COMMON_NAME, u"%s" % certdata["COMMON_NAME"]),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            keypair.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=1)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
            # Sign certificate with private key
        ).sign(keypair, hashes.SHA256())

        # Get path to save certificate
        cert_path = path.join(save_path, "certificate.pem")

        # Write certificate out to disk.
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        return