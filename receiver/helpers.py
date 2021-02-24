import socket

from lib.logger import log


def get_local_ip():
    """ 
    Returns the local host IP.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        return s.getsockname()[0]
    except Exception as ex:
        raise Exception("Local host IP couldn't be found")

def asciiart():
    log.critical("")
    log.critical("Welcome to F1 Telemetry!")
    log.critical("")
    log.critical('                     __')
    log.critical('               _.--""  |')
    log.critical(".----.     _.-'   |/\| |.--.")
    log.critical("|    |__.-'   _________|  |_)  _______________  ")
    log.critical('|  .-""-.""""" ___,    `----`"))   __   .-""-.""""--._  ')
    log.critical("'-' ,--. `    |F1L|   .---.       |:.| ' ,--. `      _`.")
    log.critical(' ( (    ) ) __|APS|__ \\\|// _..--  \/ ( (    ) )--._".-.')
    log.critical("  . `--' ;\__________________..--------. `--' ;--------'")
    log.critical("   `-..-'                               `-..-")
    log.critical("_____________________________________________________________________________________")
    log.critical("")
    log.critical("")