from lib.logger import log

class PenaltyBase:
    # Fields
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
    
    def send_to_f1laps(self):
        if not self.f1laps_api_class:
            log.error("No F1Laps API class defined for %s" % self)
            return None
        if not self.session:
            log.error("No session class defined for %s" % self)
            return None
        api = self.f1laps_api_class(self.session.f1laps_api_key, self.session.game_version)
        success = api.penalty_create(
            penalty_type = self.penalty_type,
            infringement_type = self.infringement_type,
            vehicle_index = self.vehicle_index,
            other_vehicle_index = self.other_vehicle_index,
            time_spent_gained = self.time_spent_gained,
            lap_number = self.lap_number,
            places_gained = self.places_gained,
        )
        log.info("Penalty %s successfully created in F1Laps" % self) if success else log.info("Penalty %s not created in F1Laps" % self)
        return success

    