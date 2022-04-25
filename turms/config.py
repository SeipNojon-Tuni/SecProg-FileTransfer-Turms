#   --- Turms ---
#   Cofiguration parser for Turms
#
#   Sipi Ylä-Nojonen, 2022

import configparser


class Config:
    """ Static Configuration class for reading
    user configs from file.
    """

    DEFAULT_CONFIG = {"SERVER": {"Host": "127.0.0.1",
                                 "Port": "16569",
                                 "Password": ""
                                 }}
    @staticmethod
    def get_config():
        """ Create ConfigParser object with
        configuration present in server_config.cfg file

        :return:     App configuration.
        """

        cfg = configparser.ConfigParser()

        try:
            cfg.read("./config/server_config.cfg")
            return cfg
        except:
            return Config.DEFAULT_CONFIG

    @staticmethod
    def get_server_val(name, fallb):
        """ Returns Server config field value by name.

        :param name: Config field name.
        :return:     Config field value.
        """
        cfg = Config.get_config()
        return cfg["SERVER"].get(name, fallb)
