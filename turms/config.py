#   --- Turms ---
#   Cofiguration parser for Turms
#
#   Sipi Ylä-Nojonen, 2022

import configparser
import socket
from os.path import exists
from os import mkdir

CFG_PATH = "./config/"
CFG_FILE_NAME = "./config/config.cfg"

class Config:
    """ Static Configuration class for reading
    user configs from file.
    """

    DEFAULT_CONFIG = {"TURMS": {
                         "Ip-Address": "127.0.0.1",
                         "Port": "16580",
                         "SSLPort": "16443",
                         "Xsrf": "True",
                         "AllowUnencrypted": "False",
                         "UseTLS": "True",
                         "CertPath": "./keys",
                         "AutoRemoveDamagedFile": "True"
                                 }}

    DEFAULT_CERT = {"ORGANIZATION": {
                        "CountryName": "YY",
                        "ProvinceName": "Province",
                        "LocaleName": "Locale",
                        "OrganizationName": "Org",
                        "CommonName": "127.0.0.1"
                        }
                    }

    @staticmethod
    def create_config():
        """ Create default config if doesn't exist """
        if not exists(CFG_PATH):
            mkdir(CFG_PATH)

        if not exists(CFG_FILE_NAME):
            with open(CFG_FILE_NAME, "w") as c:
                parser = configparser.ConfigParser()
                parser.read_dict(Config.DEFAULT_CONFIG)
                parser.read_dict(Config.DEFAULT_CERT)
                parser.write(c)

    @staticmethod
    def get_config():
        """ Create ConfigParser object with
        configuration present in config.cfg file

        :return:     App configuration.
        """

        cfg = configparser.ConfigParser()
        cfg.read(CFG_FILE_NAME)
        return cfg

    @staticmethod
    def get_val(sect, name, fallb):
        """ Return config value by section name and value name.

        :param sect:    Section name corresponding to python configparser / Windows ini format.
        :param name:    Config field name.
        :param fallb:   Fallback value to use if configuration is not found.
        """
        cfg = Config.get_config()
        return cfg[sect].get(name, fallb)

    @staticmethod
    def get_bool(sect, name, fallb: bool):
        """ Evaluate config value as boolean.

        :param sect:    Section name corresponding to python configparser / Windows ini format.
        :param name:    Config field name.
        :param fallb:   Fallback value to use if configuration is not found.
        """
        cfg = Config.get_config()
        return cfg[sect].getboolean(name, fallback=fallb)

    @staticmethod
    def get_turms_val(name, fallb):
        """ Returns Turms config field value by name.

        :param name:    Config field name.
        :param fallb:   Fallback value to use if none is found.
        :return:        Config field value.
        """
        return Config.get_val("TURMS", name, fallb)

    @staticmethod
    def get_organization_info():
        """ Get organization info for CSR """
        data = {"COUNTRY_NAME": Config.get_val("ORGANIZATION", "CountryName", ""),
                "PROVINCE_NAME": Config.get_val("ORGANIZATION", "ProvinceName", ""),
                "LOCALE_NAME": Config.get_val("ORGANIZATION", "LocaleName", ""),
                "ORGANIZATION_NAME": Config.get_val("ORGANIZATION", "OrganizationName", ""),
                "COMMON_NAME": Config.get_val("ORGANIZATION", "CommonName", "")}

        # Get data fields for certificate to authenticate server
        return data
