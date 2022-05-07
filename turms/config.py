#   --- Turms ---
#   Cofiguration parser for Turms
#
#   Sipi Ylä-Nojonen, 2022

import configparser
from os.path import exists

CFG_FILE_NAME = "config/config.cfg"

class Config:
    """ Static Configuration class for reading
    user configs from file.
    """

    DEFAULT_CONFIG = {"TURMS": {"Host" : "127.0.0.1",
                                 "Port" : "16569",
                                 "SSLPort" : "16443",
                                 "Xsrf" : "True",
                                 "AllowUnencrypted" : "False",
                                 "UseTLS": "True",
                                 "ChunkSize" : "1024",
                                 "CertPath" : "./keys",
                                 "AutoRemoveDamagedFile": "False"
                                 }}

    DEFAULT_CERT = { "ORGANIZATION": {
                        "CountryName" : "YY",
                        "ProvinceName ": "Province",
                        "LocaleName" : "Locale",
                        "OrganizationName" : "Org",
                        "CommonName" : "127.0.0.1"
                        }
                    }

    @staticmethod
    def create_config():
        """ Create default config if doesn't exist """
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
    def get_bool(sect, name):
        """ Evaluate config value as boolean. """
        cfg = Config.get_config()
        return cfg[sect].getboolean(name)

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
        data = {}

        # Get data fields for certificate to authenticate server
        data["COUNTRY_NAME"] = Config.get_val("ORGANIZATION", "CountryName", "")
        data["PROVINCE_NAME"] = Config.get_val("ORGANIZATION", "ProvinceName", "")
        data["LOCALE_NAME"] = Config.get_val("ORGANIZATION", "LocaleName", "")
        data["ORGANIZATION_NAME"] = Config.get_val("ORGANIZATION", "OrganizationName", "")
        data["COMMON_NAME"] = Config.get_val("ORGANIZATION", "CommonName", "")

        return data
