#   --- Turms ---
#   python logger for application
#
#   Sipi Ylä-Nojonen

import logging
import sys


def create_logger():
    """
    Create logger and handles to file and
    GUI log output for application
    using pythons logging library
    """

    logger = logging.getLogger("turms.logger")
    logger.setLevel(logging.INFO)

    log_name = "./logs/turms-latest.log"

    file_handler = logging.FileHandler(log_name)
    file_handler.setLevel(logging.INFO)

    errhandler = logging.StreamHandler(sys.stderr)
    errhandler.setLevel(logging.WARNING)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("<%(asctime)s> %(name)s - %(levelname)s - %(message)s")
    console_formatter = logging.Formatter("<%(asctime)s> %(levelname)s: %(message)s")

    file_handler.setFormatter(formatter)
    errhandler.setFormatter(formatter)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(errhandler)
    return logger


def create_debug_logger():
    logger = logging.getLogger("debug_logger")
    logger.setLevel(logging.DEBUG)


def get():
    return logging.getLogger("turms.logger")


# TODO: SANITIZE LOGGING INPUT

# Shortcuts for different levels of logging
# with 'getLogger("turms.logger").method(msg)'
def log(lvl, msg):
    get().log(level=lvl, msg=msg)


def info(msg):
    get().info(msg)


def warning(msg):
    get().warning(msg)


def error(msg):
    get().error(msg)


