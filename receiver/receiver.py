import threading
import socket
import sentry_sdk
import platform

from lib.logger import log
from receiver.f12020.processor import F12020Processor
from receiver.f12021.processor import F12021Processor
from receiver.helpers import get_local_ip
from receiver.game_version import parse_game_version_from_udp_packet
import config


DEFAULT_PORT = 20777
SENTRY_DSN = "https://d00edba104864bee975f5f4a71025639@o615967.ingest.sentry.io/5854730"


class ActiveSocket:
    socket = None


class RaceReceiver(threading.Thread):

    def __init__(self, f1laps_api_key, enable_telemetry=True, host_ip=None, host_port=None, run_as_daemon=True):
        """
        Init the receiver with all attributes needed to 
        push data to F1Laps
        """

        super(RaceReceiver, self).__init__()

        # For the UI app, the thread needs to be a daemon so we can easily quit it
        # With normal thread, Python wont stop our loop
        # For CLI, we need a normal thread in order to directly control it
        self.daemon = run_as_daemon
        # Also, we need a way to kill it - which isn't easy
        # Best way I've found so far is an Event that can be set
        self.kill_event = threading.Event()

        # Network settings
        self.host_ip   = host_ip or get_local_ip()
        self.host_port = host_port or int(DEFAULT_PORT)

        log.info("*************************************************")
        log.info("Set your F1 game telemetry IP to:   %s" % self.host_ip)
        log.info("Set your F1 game telemetry port to: %s" % self.host_port)
        log.info("*************************************************")

        # Get previously opened socket, or create new one
        self.udp_socket = self.get_socket()

        # f1laps api key and settings
        self.f1laps_api_key = f1laps_api_key
        self.telemetry_enabled = enable_telemetry

        # game data processor
        self.processor = None

        # Start sentry
        self.start_sentry()
 
        log.info("Telemetry receiver started & ready for race data")


    def start_sentry(self):
        sentry_sdk.init(
            SENTRY_DSN,
            traces_sample_rate=0,
            release=config.VERSION
        )
        sentry_sdk.set_context("machine", {
            "system": platform.system(),
            "release": platform.release()
        })
        sentry_sdk.set_context("api", {
            "key": self.f1laps_api_key,
            "telemetry_enabled": self.telemetry_enabled
        })


    def get_socket(self):
        """ Get ActiveSocket or initiate it """
        if not ActiveSocket.socket:
            new_socket = self.open_socket()
            ActiveSocket.socket = new_socket
            return new_socket
        else:
            return ActiveSocket.socket


    def open_socket(self):
        new_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # The SO_REUSEADDR setting allows us to reuse sockets
        # Which may be necessary when a user restarts sessions
        # See https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more details
        if True or self.use_udp_broadcast:
            # Enable broadcasting mode
            log.info("Using UDP broadcast mode")
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)    
            new_socket.bind(("", self.host_port))
        else:
            log.info("Using UDP unicast mode")
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            new_socket.bind((self.host_ip, self.host_port))
        log.debug("Socket opened and bound")
        return new_socket


    def kill(self):
        self.kill_event.set()
        log.info("Telemetry receiver stopped")

    
    def run(self):
        """
        This method is called automatically when calling .start() on the receiver class (in race.py). 
        The caller should call .start() to not get stuck in the while True loop

        It's the main packet listening method.
        """
        # Starting an endless loop to continuously listen for UDP packets
        # until user aborts or process is terminated
        log.info("Receiver started running")
        
        while not self.kill_event.is_set():
            try:
                incoming_udp_packet = self.udp_socket.recv(2048)
                # Get game version -- raises if unknown or not found
                # Do this for every packet so that we can handle game switches in flight
                game_version = parse_game_version_from_udp_packet(incoming_udp_packet)
                if game_version == "f12020":
                    # Only start processor if it's not set yet or has switched
                    if not self.processor or not isinstance(self.processor, F12020Processor):
                        log.info("Detected F1 2020 game version, starting F1 2020 processor.")
                        self.processor = F12020Processor(self.f1laps_api_key, self.telemetry_enabled)
                elif game_version == "f12021":
                    # Only start processor if it's not set yet or has switched
                    if not self.processor or not isinstance(self.processor, F12021Processor):
                        log.info("Detected F1 2021 game version, starting F1 2021 processor.")
                        self.processor = F12021Processor(self.f1laps_api_key, self.telemetry_enabled)
                else:
                    log.info("Unknown packet or game version.")
                if self.processor:
                    self.processor.process(incoming_udp_packet)
            except Exception as ex:
                log.info(ex)
                sentry_sdk.capture_exception(ex)
            

