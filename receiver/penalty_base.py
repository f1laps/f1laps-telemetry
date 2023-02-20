from lib.logger import log


class PenaltyBase:
    # Fields
    frame_id = None
    penalty_type = None
    infringement_type = None
    vehicle_index = None
    other_vehicle_index = None
    time_spent_gained = None
    lap_number = None
    places_gained = None
    # Link to session, needed for API call
    session = None
    # Link to API class, update with current version
    f1laps_api_class = None

    def __str__(self):
        return "Penalty (type %s, infringement %s, vehicle %s, lap %s)" % (
            self.penalty_type,
            self.infringement_type,
            self.vehicle_index,
            self.lap_number
            ) 
        
    def add_to_lap(self):
        """ Add a newly created Penalty to the current lap """
        # A penalty should always have a session, but just in case...
        if not self.session:
            log.error("No session defined for %s" % self)
            return None
        # For F1 2021, lap_list is still a freestyle dict
        # For F1 2022+, it's an array of a class
        if self.session.game_version == "f12021":
            lap = self.session.lap_list[self.lap_number]
            # We might not have the penalties array yet, let's create it if not
            if not lap.get("penalties"):
                lap["penalties"] = []
            lap["penalties"].append(self)
        else:
            lap = self.session.lap_list.get(self.lap_number)
            if lap:
                lap.penalties.append(self)
            else:
                # Penalty couldn't be added because lap doesn't exist
                # Can happen e.g. when pausing mid-session and restarting
                # We're not solving for this use case for now
                log.info("Penalty couldn't be added to lap %s" % self.lap_number)
    
    def json_serialize(self):
        """ Convert object to JSON """
        return {
            "frame_id": self.frame_id,
            "penalty_type": self.penalty_type,
            "infringement_type": self.infringement_type,
            "vehicle_index": self.vehicle_index,
            "other_vehicle_index": self.other_vehicle_index,
            "time_spent_gained": self.time_spent_gained,
            "lap_number": self.lap_number,
            "places_gained": self.places_gained,
        }
    