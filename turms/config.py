#   --- Turms ---
#   Cofiguration parser for Turms
#
#   Sipi Ylä-Nojonen, 2022

import configparser

def create_config():
    """ Create ConfigParser object with
    configuration present in server_config.cfg file """

    cfg = configparser.ConfigParser()

    try:
        cfg.read("./config/server_config.cfg")
        return cfg
    except:
        return {"SERVER": { "Host" : "127.0.0.1",
                            "Port" : "16569",
                            "Password" : ""
                             }}

