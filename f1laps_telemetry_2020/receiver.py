import socket
import multiprocessing
import f1_2020_telemetry.packets

from lib.logger import log
from f1laps_telemetry_2020.packets import SessionPacket, ParticipantsPacket, CarSetupPacket, \
                                          FinalClassificationPacket, LapPacket, CarStatusPacket
from f1laps_telemetry_2020.helpers import get_local_ip


DEFAULT_PORT = 20777


class RaceReceiver(multiprocessing.Process):

    def __init__(self, f1laps_api_key, host_ip=None, host_port=None):
        """
        Init the receiver with all attributes needed to 
        push data to F1Laps
        """

        super(RaceReceiver, self).__init__()

        # Network settings
        self.host_ip   = host_ip or get_local_ip()
        self.host_port = host_port or int(DEFAULT_PORT)

        log.warning("")
        log.warning("*************************************************")
        log.warning("Set your F1 game telemetry IP to:   %s" % self.host_ip)
        log.warning("Set your F1 game telemetry port to: %s" % self.host_port)
        log.warning("*************************************************")
        log.warning("")

        # Bind socket
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_socket.bind((self.host_ip, self.host_port))

        # local session session
        self.session = None

        # f1laps api key
        self.f1laps_api_key = f1laps_api_key


    def kill(self):
        self.terminate()
        self.udp_socket.close()
        log.info("Race Receiver process has been terminated")
        
    
    def run(self):
        """
        This method is called automatically when calling .start() on the receiver class (in race.py). 
        The caller should call .start() to not get stuck in the while True loop

        It's the main packet listening method.
        """
        # Starting an endless loop to continuously listen for UDP packets
        # until user aborts or process is terminated
        log.info("Telemetry data receiver is now running successfully")
        
        while True:
            incoming_udp_packet = self.udp_socket.recv(2048)
            packet = f1_2020_telemetry.packets.unpack_udp_packet(incoming_udp_packet)

            # process session packets first
            # the session packet class returns a session object 
            # it doesn't change the session for existing sessions
            # it returns a new session object for new sessions
            if isinstance(packet, f1_2020_telemetry.packets.PacketSessionData_V1):
                self.session = SessionPacket().process(packet, self.session)
                self.session.f1laps_api_key = self.f1laps_api_key

            # dont do anything else if there isnt a session set
            if self.session:

                # Now we listen to the actual race information
                # Each package gets processed in real-time as it comes in

                # Participants
                if isinstance(packet, f1_2020_telemetry.packets.PacketParticipantsData_V1):
                    ParticipantsPacket().process(packet, self.session)

                # Setup
                if isinstance(packet, f1_2020_telemetry.packets.PacketCarSetupData_V1):
                    CarSetupPacket().process(packet, self.session)

                # Lap Data
                if isinstance(packet, f1_2020_telemetry.packets.PacketLapData_V1):
                    LapPacket().process(packet, self.session)

                # Car Status Data
                if isinstance(packet, f1_2020_telemetry.packets.PacketCarStatusData_V1):
                    CarStatusPacket().process(packet, self.session)

                # Final Classification
                if isinstance(packet, f1_2020_telemetry.packets.PacketFinalClassificationData_V1):
                    FinalClassificationPacket().process(packet, self.session)

