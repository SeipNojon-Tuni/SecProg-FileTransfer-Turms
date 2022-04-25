#   --- Turms ---
#   python logger for application
#
#   Sipi Ylä-Nojonen

import logging
import sys
from config import Config as cfg

DEFAULT_LOG = "./logs/turms-latest.log"
DEFAULT_SERVER_LOG = "./logs/turms-server.log"


class TurmsLogger:

    @staticmethod
    def create_logger():
        """
        Set up logger and handles to file and
        GUI log output for application
        using pythons logging library.
        """

        logger = logging.getLogger("turms.logger")
        logger.setLevel(logging.INFO)

        log_name = DEFAULT_LOG

        # Route logging stream to GUI console output and
        # to two separate files: One for server logger,
        # one for other logging.

        file_handler = logging.FileHandler(log_name)
        file_handler.setLevel(logging.INFO)

        errhandler = logging.StreamHandler(sys.stderr)
        errhandler.setLevel(logging.WARNING)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter("<%(asctime)s> %(name)s - %(levelname)s - %(message)s")

        console_formatter = logging.Formatter("<%(asctime)s> %(levelname)s: %(message)s")
        sconsole_formatter = logging.Formatter("<%(asctime)s> -SERVER- %(levelname)s: %(message)s")

        file_handler.setFormatter(formatter)
        errhandler.setFormatter(formatter)
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(errhandler)

        TurmsLogger.info("Application logger setup finished.")

        # Add server logging to separate file and GUI console
        server_log = DEFAULT_SERVER_LOG
        sf_handler = logging.FileHandler(server_log)
        sc_handler = logging.StreamHandler(sys.stdout)
        sf_handler.setFormatter(formatter)
        sc_handler.setFormatter(sconsole_formatter)

        acc_logger = logging.getLogger("tornado.access")
        app_logger = logging.getLogger("tornado.application")
        gen_logger = logging.getLogger("tornado.general")
        acc_logger.addHandler(sf_handler)
        acc_logger.addHandler(sc_handler)

        app_logger.addHandler(sf_handler)
        app_logger.addHandler(sc_handler)

        gen_logger.addHandler(sf_handler)
        gen_logger.addHandler(sc_handler)

        return logger

    @staticmethod
    def set_log_level(level):
        """
        Set level of the logger to ignore certain levels of information.

        :param level: Level of logger to set. Should correspond to python logging levels.
        :return:
        """
        try:
            logging.getLogger("turms.logger").setLevel(level)
        except ValueError:
            TurmsLogger.warning("Undefined level for logger.")

    # Shortcuts for different levels of logging
    # with 'getLogger(name).method(msg)'

    @staticmethod
    def log(lvl, msg, name="turms.logger"):
        """ Short cut for python logging.getLogger(name).log(msg) """
        logging.getLogger(name).log(level=lvl, msg="%s" % msg)

    @staticmethod
    def info(msg, name="turms.logger"):
        """ Short cut for python logging.getLogger(name).info(msg) """
        logging.getLogger(name).info("%s" % msg)

    @staticmethod
    def warning(msg, name="turms.logger"):
        """ Short cut for python logging.getLogger(name).warning(msg) """
        logging.getLogger(name).warning("%s" % msg)

    @staticmethod
    def error(msg, name="turms.logger"):
        """ Short cut for python logging.getLogger(name).error(msg) """
        logging.getLogger(name).error("%s" % msg)





