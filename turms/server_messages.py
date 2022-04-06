
from datetime import datetime


def get_current_time():
    return datetime.now().strftime(fmt="%Y-%m-%d - %H:%M:%S")


SERVER_HELLO = "Hello from server. "