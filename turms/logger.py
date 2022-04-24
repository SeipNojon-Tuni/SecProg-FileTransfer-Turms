#   --- Turms ---
#   python logger for application
#
#   Sipi Ylä-Nojonen

import logging
import sys

DEFAULT_LOG = "./logs/turms-latest.log"
DEFAULT_SERVER_LOG = "./logs/turms-server.log"

def create_logger():
    """
    Create logger and handles to file and
    GUI log output for application
    using pythons logging library
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

    info("Application logger setup finished.")

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


def set_log_level(level):
    """
    set level of .

    :param console: Boolean to determine whether to print log to scree console.
    :return:
    """
    try:
        logging.getLogger("turms.logger").setLevel(level)
    except ValueError:
        warning("Undefined level for logger.")

# TODO: SANITIZE LOGGING INPUT

# Shortcuts for different levels of logging
# with 'getLogger(name).method(msg)'
def log(lvl, msg, name="turms.logger"):
    logging.getLogger(name).log(level=lvl, msg="%s" % msg)


def info(msg, name="turms.logger"):
    logging.getLogger(name).info("%s" % msg)


def warning(msg, name="turms.logger"):
    logging.getLogger(name).warning("%s" % msg)


def error(msg, name="turms.logger"):
    logging.getLogger(name).error("%s" % msg)





