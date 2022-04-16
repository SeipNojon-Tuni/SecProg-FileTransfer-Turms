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
from pathvalidate import sanitize_filename, validate_filename

CONTENT_PATH = "./content"

def raw_server_content():
    # From content directory get files and not directories.
    onlyfiles = [f for f in listdir(CONTENT_PATH) if isfile(join(CONTENT_PATH, f))]
    return onlyfiles

def fetch_server_content():
    # From content directory get files and not directories.
    onlyfiles = raw_server_content()

    jsonStr = json.dumps(onlyfiles)
    return jsonStr


def get_file_object(filename):
    """ Sanitize passed filename and try to find server
    content that corresponds to requested file. """

    # Sanitize file name and remove any illegal
    # characters to prevent f.e. directory traversal.
    san_name = sanitize_filename(filename)

    # Validate filename
    validate_filename(san_name)

    # Open file to be read as bytes for server send to user
    if not san_name in raw_server_content():
        return None

    path = CONTENT_PATH + "/" + san_name
    file = open(path, "rb")
    return file
