#   --- Turms ---
#   Implementation for handling and
#   providing user with download options
#   and server content information
#   server side.
#
#   Sipi Ylä-Nojonen, 2022

from os import listdir
from os.path import isfile, join
import json

CONTENT_PATH = "./content"


def fetch_server_content():
    # From content directory get files and not directories.
    onlyfiles = [f for f in listdir(CONTENT_PATH) if isfile(join(CONTENT_PATH, f))]

    jsonStr = json.dumps(onlyfiles)
    return jsonStr


def get_file_object(filename):

    # TODO: Escape illegal characters from filename such as slashes to prevent tree traversal
    safename = ""

    # Open file to be read as bytes for server send to user
    path = CONTENT_PATH + "/" + safename
    file = open(path, "rb")
    return file