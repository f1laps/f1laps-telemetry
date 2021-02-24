from receiver.session import Session
from lib.logger import log


class SessionPacket:
    """ Process session packets """
    def process(self, packet, session):
        """
        Session info is unique. Create new if it changed, or do nothing.
        """
        if not session or (session.session_udp_uid != packet.header.sessionUID):
            return self.create_session(packet, session)
        else:
            return self.update_session(packet, session)

    def create_session(self, packet, session):
        packet_session_uid = packet.header.sessionUID
        session = Session(session_uid=packet_session_uid)
        session.session_type = packet.sessionType
        session.track_id = packet.trackId
        if packet.weather not in session.weather_ids:
            session.weather_ids.append(packet.weather)
        log.info("*************************************************")
        log.info("New session started: %s %s (ID %s)" % (session.get_track_name(), 
                                                            session.map_udp_session_id_to_f1laps_token(),
                                                            packet_session_uid))
        log.info("*************************************************")
        return session

    def update_session(self, packet, session):
        packet_session_uid = packet.header.sessionUID
        if packet.weather not in session.weather_ids:
            session.weather_ids.append(packet.weather)
        return session

class LapPacket:
    """ Process lap packets """
    def process(self, packet, session):
        """
        Lap data changes throughout each lap
        So we always update the local session object
        """
        lap_data = packet.lapData[packet.header.playerCarIndex]

        # For new sessions, set the current lap number with the first packet
        if session.lap_number_current is None:
            session.lap_number_current = lap_data.currentLapNum

        # Check if we started a new lap
        new_lap_started = (session.lap_number_current != lap_data.currentLapNum)

        # Set session current lap to this lap
        session.lap_number_current = lap_data.currentLapNum
            
        # initiate lap data in the lap list array if necessary
        if not session.lap_list.get(session.lap_number_current):
            session.lap_list[session.lap_number_current] = {}

        # Always update the session lap list
        session = self.update_session(packet, session, lap_number=session.lap_number_current)

        # If we're on a new lap, we calculate the final last lap data and then push to F1Laps
        if new_lap_started:
            last_lap_number = session.lap_number_current - 1
            log.info("*************************************************")
            log.info("New lap #%s started" % session.lap_number_current)
            log.info("Lap time of last lap #%s: %s" % (last_lap_number, lap_data.lastLapTime))
            log.info("*************************************************")
            
            # Check if we know about the last lap 
            # (maybe the user just started this script in the middle of the session)
            if session.lap_list.get(last_lap_number):
                # re-calculate sector 3 with the final times we have now
                session = self.update_session_last_lap(packet, session, last_lap_number=last_lap_number)

                # We want to only send full laps to F1Laps. But Telemetry doesn't tell us full laps
                # So we send to F1Laps if the lap has a sector 2 time, which we assume means it's complete
                # Sector 3 is not a good proxy because its time gets calculated in real time in our code
                # We can probably improve this by using the motion packet data instead
                if session.lap_list[last_lap_number]["sector_2_time_ms"] > 0:
                    self.process_lap_in_f1laps(session, last_lap_number)

        return session

    def update_session(self, packet, session, lap_number):
        lap_data = packet.lapData[packet.header.playerCarIndex]

        # The lap packet doesn't have the sector 3 time
        # So we always calculate it over the course of a lap in real-time
        total_lap_time = lap_data.currentLapTime * 1000 # current lap time is in secs not ms
        sector_3_time = total_lap_time - lap_data.sector1TimeInMS - lap_data.sector2TimeInMS

        # pit status changes over the course of a lap
        # we want to keep the highest number of 
        # 0 = no pit; 1 = pit entry/exit; 2 = pitting
        # so that we store the "slowest" pit value\
        if session.lap_list[lap_number].get("pit_status"):
            pit_status = max(session.lap_list[lap_number]["pit_status"], lap_data.pitStatus)
        else:
            pit_status = lap_data.pitStatus

        # now update the session's lap list array with the current lap data 
        session.lap_list[lap_number]["sector_1_time_ms"]  = lap_data.sector1TimeInMS
        session.lap_list[lap_number]["sector_2_time_ms"]  = lap_data.sector2TimeInMS
        session.lap_list[lap_number]["sector_3_time_ms"]  = round(sector_3_time)
        session.lap_list[lap_number]["lap_number"]        = lap_data.currentLapNum
        session.lap_list[lap_number]["car_race_position"] = lap_data.carPosition
        session.lap_list[lap_number]["pit_status"]        = pit_status
        
        return session

    def update_session_last_lap(self, packet, session, last_lap_number):
        lap_data = packet.lapData[packet.header.playerCarIndex]
        # re-calculate sector 3 time again, just in case
        last_lap_total_time    = lap_data.lastLapTime * 1000 # last lap is in secs not ms
        last_lap_sector_1_time = session.lap_list[last_lap_number]['sector_1_time_ms']
        last_lap_sector_2_time = session.lap_list[last_lap_number]['sector_2_time_ms']
        last_lap_sector_3_time = last_lap_total_time - last_lap_sector_1_time - last_lap_sector_2_time
        # add last lap sector 3 time to lap list
        session.lap_list[last_lap_number]['sector_3_time_ms'] = round(last_lap_sector_3_time)
        return session

    def process_lap_in_f1laps(self, session, lap_number):
        log.debug("Creating lap #%s in F1Laps" % lap_number)
        return session.process_lap_in_f1laps(lap_number)


class CarStatusPacket:
    """ Process car status packets """
    def process(self, packet, session):
        """
        We get tyre info from this packet
        Store it continuously
        """
        return self.update_session(packet, session)

    def update_session(self, packet, session):
        car_status = packet.carStatusData[packet.header.playerCarIndex]
        if session.lap_number_current is not None and session.lap_list.get(session.lap_number_current):
            session.lap_list[session.lap_number_current]['tyre_compound_visual'] = car_status.visualTyreCompound
        return session


class ParticipantsPacket:
    """ Process participants packets """
    def process(self, packet, session):
        """
        Track is unique to a session. Only set it once.
        """
        if session.team_id:
            return False
        else:
            session = self.update_session(packet, session)
            return session

    def update_session(self, packet, session):
        team_id          = packet.participants[packet.header.playerCarIndex].teamId
        session.team_id  = team_id
        return session
        

class CarSetupPacket:
    """ Process car setup packets """
    def process(self, packet, session):
        """ 
        Setup data can change throughout the session
        So we always update the local session object
        """
        return self.update_session(packet, session)

    def update_session(self, packet, session):
        setup_data = packet.carSetups[packet.header.playerCarIndex]
        session.setup['front_wing']                   = setup_data.frontWing
        session.setup['rear_wing']                    = setup_data.rearWing
        session.setup['diff_adjustment_on_throttle']  = setup_data.onThrottle
        session.setup['diff_adjustment_off_throttle'] = setup_data.offThrottle
        session.setup['front_camber']                 = setup_data.frontCamber
        session.setup['rear_camber']                  = setup_data.rearCamber
        session.setup['front_toe']                    = setup_data.frontToe
        session.setup['rear_toe']                     = setup_data.rearToe
        session.setup['front_suspension']             = setup_data.frontSuspension
        session.setup['rear_suspension']              = setup_data.rearSuspension
        session.setup['front_antiroll_bar']           = setup_data.frontAntiRollBar
        session.setup['rear_antiroll_bar']            = setup_data.rearAntiRollBar
        session.setup['front_ride_height']            = setup_data.frontSuspensionHeight
        session.setup['rear_ride_height']             = setup_data.rearSuspensionHeight
        session.setup['brake_pressure']               = setup_data.brakePressure
        session.setup['front_brake_bias']             = setup_data.brakeBias
        session.setup['front_right_tyre_pressure']    = setup_data.frontRightTyrePressure
        session.setup['front_left_tyre_pressure']     = setup_data.frontLeftTyrePressure
        session.setup['rear_right_tyre_pressure']     = setup_data.rearRightTyrePressure
        session.setup['rear_left_tyre_pressure']      = setup_data.rearLeftTyrePressure
        return session


class FinalClassificationPacket:
    """ Process final classification packets """
    def process(self, packet, session):
        """ 
        Comes in once at the end of a session
        """
        session = self.update_session(packet, session)
        self.process_in_f1laps(session)
        return session

    def update_session(self, packet, session):
        classification_data     = packet.classificationData[packet.header.playerCarIndex]
        session.finish_position = classification_data.position
        session.result_status   = classification_data.resultStatus
        session.points          = classification_data.points
        return session

    def process_in_f1laps(self, session):
        log.debug("Creating session in F1Laps")
        return session.process_lap_in_f1laps()



