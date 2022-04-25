#   --- Turms ---
#   Cofiguration parser for Turms
#
#   Sipi Ylä-Nojonen, 2022

import configparser

CFG_FILE_NAME = "./config/config.cfg"

class Config:
    """ Static Configuration class for reading
    user configs from file.
    """

    DEFAULT_CONFIG = {"SERVER": {"Host" : "127.0.0.1",
                                 "Port" : "16569",
                                 "Password" : "",
                                 "AllowUnencrypted" : "False"
                                 }}
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
    def get_server_val(name, fallb):
        """ Returns Server config field value by name.

        :param name:    Config field name.
        :param fallb:   Fallback value to use if none is found.
        :return:        Config field value.
        """
        return Config.get_val("SERVER", name, fallb)
