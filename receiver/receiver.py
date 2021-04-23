import threading
import socket
import f1_2020_telemetry.packets

from lib.logger import log
from receiver.packets import SessionPacket, ParticipantsPacket, CarSetupPacket, \
                             FinalClassificationPacket, LapPacket, CarStatusPacket, \
                             TelemetryPacket, MotionPacket
from receiver.helpers import get_local_ip


DEFAULT_PORT = 20777


class ActiveSocket:
    socket = None


class RaceReceiver(threading.Thread):

    def __init__(self, f1laps_api_key, host_ip=None, host_port=None, run_as_daemon=True):
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

        log.debug("*************************************************")
        log.debug("Set your F1 game telemetry IP to:   %s" % self.host_ip)
        log.debug("Set your F1 game telemetry port to: %s" % self.host_port)
        log.debug("*************************************************")

        # Get previously opened socket, or create new one
        self.udp_socket = self.get_socket()
        
        # local session session
        self.session = None

        # f1laps api key
        self.f1laps_api_key = f1laps_api_key
 
        log.info("Telemetry receiver started & ready for race data")


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
        # I'm not 100% sure though
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
        log.debug("Receiver started running")
        
        while not self.kill_event.is_set():
            incoming_udp_packet = self.udp_socket.recv(2048)
            packet = f1_2020_telemetry.packets.unpack_udp_packet(incoming_udp_packet)

            # process session packets first
            # the session packet class returns a session object 
            # it doesn't change the session for existing sessions
            # it returns a new session object for new sessions
            if isinstance(packet, f1_2020_telemetry.packets.PacketSessionData_V1):
                self.session = SessionPacket().process(packet, self.session)
                if self.session:
                    self.session.f1laps_api_key = self.f1laps_api_key

            # dont do anything else if there isnt a session set
            if self.session:

                # Now we listen to the actual race information
                # Each package gets processed in real-time as it comes in

                # Participants
                if isinstance(packet, f1_2020_telemetry.packets.PacketParticipantsData_V1):
                    ParticipantsPacket().process(packet, self.session)

                # Motion
                if isinstance(packet, f1_2020_telemetry.packets.PacketMotionData_V1):
                    MotionPacket().process(packet, self.session)

                # Setup
                if isinstance(packet, f1_2020_telemetry.packets.PacketCarSetupData_V1):
                    CarSetupPacket().process(packet, self.session)

                # Lap Data
                if isinstance(packet, f1_2020_telemetry.packets.PacketLapData_V1):
                    LapPacket().process(packet, self.session)

                # Car Status Data
                if isinstance(packet, f1_2020_telemetry.packets.PacketCarStatusData_V1):
                    CarStatusPacket().process(packet, self.session)

                # Telemetry Data
                if isinstance(packet, f1_2020_telemetry.packets.PacketCarTelemetryData_V1):
                    TelemetryPacket().process(packet, self.session)

                # Final Classification
                if isinstance(packet, f1_2020_telemetry.packets.PacketFinalClassificationData_V1):
                    FinalClassificationPacket().process(packet, self.session)

