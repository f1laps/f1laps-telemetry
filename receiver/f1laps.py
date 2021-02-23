import requests


class F1LapsAPI:
    """ Communicate with F1Laps API """

    def __init__(self, api_key):
        self.api_key  = api_key
        self.base_url = 'https://www.f1laps.com/api/'

    def call_api(self, method, endpoint, params=None):
        headers = {
            'Content-Type' : 'application/json',
            'Authorization': 'Token %s' % self.api_key
        }
        if method == "GET":
            return requests.get(endpoint , headers=headers)
        elif method == "POST":
            return requests.post(endpoint, headers=headers, json=params)
        elif method == "PUT":
            return requests.put(endpoint , headers=headers, json=params)

    def lap_create(self, track_id, team_id, conditions, game_mode, 
                   sector_1_time, sector_2_time, sector_3_time, setup_data):
        """ Create a Lap in F1Laps """
        endpoint = self.base_url + "f12020/laps/"
        method   = "POST"
        params   = {
            'track': track_id,
            'team': team_id,
            'conditions': conditions,
            'game_mode': game_mode,
            'sector_1_time_ms': sector_1_time,
            'sector_2_time_ms': sector_2_time,
            'sector_3_time_ms': sector_3_time,
            'setup': setup_data
        }
        return self.call_api(method, endpoint, params)

    def session_create(self, track_id, team_id, session_uid, conditions, session_type, 
                       finish_position, points, result_status, lap_times, setup_data):
        """ Create a Session in F1Laps """
        endpoint = self.base_url + "f12020/grandprixs/sessions/"
        method   = "POST"
        params   = {
            'track': track_id,
            'team': team_id,
            'conditions': conditions,
            'session_type': session_type,
            'finish_position': finish_position,
            'points': points,
            'result_status': result_status,
            'udp_session_uid': session_uid,
            'lap_times': lap_times,
            'setup': setup_data
        }
        return self.call_api(method, endpoint, params)

    def session_update(self, f1laps_session_id, track_id, team_id, session_uid, conditions, 
                       session_type, finish_position, points, result_status, lap_times, 
                       setup_data):
        """ Update a Session in F1Laps """
        endpoint = "%sf12020/grandprixs/sessions/%s/" % (self.base_url, f1laps_session_id)
        method   = "PUT"
        params   = {
            'track': track_id,
            'team': team_id,
            'conditions': conditions,
            'session_type': session_type,
            'finish_position': finish_position,
            'points': points,
            'result_status': result_status,
            'udp_session_uid': session_uid,
            'lap_times': lap_times,
            'setup': setup_data
        }
        return self.call_api(method, endpoint, params)

    def session_list(self, session_uid):
        """
        List sessions in F1Laps, filtered by UDP session ID
        """
        endpoint = self.base_url + "f12020/grandprixs/sessions/?udp_session_uid=%s" % session_uid
        method   = "GET"
        return self.call_api(method, endpoint)



