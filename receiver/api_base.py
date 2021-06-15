import platform
import requests

import config


class F1LapsAPIBase:
    """ Communicate with F1Laps API """

    def __init__(self, api_key, game_version):
        self.api_key  = api_key
        self.base_url = 'https://www.f1laps.com/api/'
        self.version  = config.VERSION
        self.game_version = game_version

    def call_api(self, method, endpoint, params=None):
        headers = self._get_headers()
        path = self.base_url + self.game_version + "/" + endpoint 
        if method == "GET":
            return requests.get(path , headers=headers)
        elif method == "POST":
            return requests.post(path, headers=headers, json=params)
        elif method == "PUT":
            return requests.put(path , headers=headers, json=params)

    def lap_create(self, track_id, team_id, conditions, game_mode, 
                   sector_1_time, sector_2_time, sector_3_time, setup_data, 
                   is_valid, telemetry_data_string):
        """ Create a Lap in F1Laps """
        endpoint = "laps/"
        method   = "POST"
        params   = {
            'track': track_id,
            'team': team_id,
            'conditions': conditions,
            'game_mode': game_mode,
            'sector_1_time_ms': sector_1_time,
            'sector_2_time_ms': sector_2_time,
            'sector_3_time_ms': sector_3_time,
            'setup': setup_data,
            'is_valid': is_valid,
            'telemetry_data_string': telemetry_data_string
        }
        return self.call_api(method, endpoint, params)

    def session_create(self, track_id, team_id, session_uid, conditions, session_type, 
                       finish_position, points, result_status, lap_times, setup_data,
                       is_online_game):
        """ Create a Session in F1Laps """
        endpoint = "grandprixs/sessions/"
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
            'setup': setup_data,
            'is_online_game': is_online_game
        }
        return self.call_api(method, endpoint, params)

    def session_update(self, f1laps_session_id, track_id, team_id, session_uid, conditions, 
                       session_type, finish_position, points, result_status, lap_times, 
                       setup_data, is_online_game):
        """ Update a Session in F1Laps """
        endpoint = "grandprixs/sessions/%s/" % f1laps_session_id
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
            'setup': setup_data,
            'is_online_game': is_online_game
        }
        return self.call_api(method, endpoint, params)

    def session_list(self, session_uid):
        """
        List sessions in F1Laps, filtered by UDP session ID
        """
        endpoint = "grandprixs/sessions/?udp_session_uid=%s" % session_uid
        method   = "GET"
        return self.call_api(method, endpoint)

    def _get_headers(self):
        return {
            'Content-Type'      : 'application/json',
            'Authorization'     : 'Token %s' % self.api_key,
            'X-F1Laps-App'      : 'F1Laps Telemetry v%s' % self.version,
            'X-F1Laps-Platform' : self._get_platform()
        }

    def _get_platform(self):
        return "%s %s" % (platform.system(), platform.release())



