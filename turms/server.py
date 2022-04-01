#   --- Turms ---
#   Handling for server system to delegate
#   request handlers for user connections
#
#   Sipi Ylä-Nojonen, 2022



#   By default use port that is unassigned by IANA
#   and not known to be widely used by other applications.
#   according to listing such as:
#       https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
#       https://www.speedguide.net/port.php?port=16568
DEFAULT_PORT = 16569

class TurmsServer():
    def __init__(self):
        super()

