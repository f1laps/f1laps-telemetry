import platform
import requests
import json

import config
from lib.logger import log


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
            return self.call_api_get(path , headers=headers)
        elif method == "POST":
            return self.call_api_post(path, headers=headers, json=params)
        elif method == "PUT":
            return self.call_api_put(path , headers=headers, json=params)

    def call_api_get(self, path, headers):
        try:
            return requests.get(path , headers=headers)
        except requests.ConnectionError as ex:
            log.info("ConnectionError calling %s: %s" % (path, ex))
            return None

    def call_api_post(self, path, headers, json):
        try:
            return requests.post(path, headers=headers, json=json)
        except requests.ConnectionError as ex:
            log.info("ConnectionError calling %s: %s" % (path, ex))
            return None

    def call_api_put(self, path, headers, json):
        try:
            return requests.put(path , headers=headers, json=json)
        except requests.ConnectionError as ex:
            log.info("ConnectionError calling %s: %s" % (path, ex))
            return None


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
        response = self.call_api(method, endpoint, params)
        self._log_f1laps_response_status(response, descriptor="Lap_create")
        return 

    def session_create(self, track_id, team_id, session_uid, conditions, session_type, 
                       finish_position, points, result_status, lap_times, setup_data,
                       is_online_game, **extra_params):
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
            'is_online_game': is_online_game,
            **extra_params
        }
        return self.call_api(method, endpoint, params)

    def session_update(self, f1laps_session_id, track_id, team_id, session_uid, conditions, 
                       session_type, finish_position, points, result_status, lap_times, 
                       setup_data, is_online_game, **extra_params):
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
            'is_online_game': is_online_game,
            **extra_params
        }
        return self.call_api(method, endpoint, params)

    def session_list(self, session_uid):
        """
        List sessions in F1Laps, filtered by UDP session ID
        """
        endpoint = "grandprixs/sessions/?udp_session_uid=%s" % session_uid
        method   = "GET"
        return self.call_api(method, endpoint)

    def session_create_or_update(self, **kwargs):
        """
        Wrapper function around session_create and session_update
        Returns:
            success (bool)
            f1laps_session_id (char)
        """
        f1_laps_session_id = kwargs.get('f1laps_session_id')
        success = False
        if not f1_laps_session_id:
            # Create session
            kwargs_exclude_in_create = ['f1laps_session_id']
            session_create_params = {k:v for k,v in kwargs.items() if k not in kwargs_exclude_in_create}
            response = self.session_create(**session_create_params)
            if response is None:
                # API call failed, e.g. due to Connection Error
                log.info("API call failed - not updating in F1Laps")
                success = False
            elif response.status_code == 201:
                log.info("Session successfully created in F1Laps")
                f1_laps_session_id = json.loads(response.content)['id']
                success = True
            else:
                # The call may have failed because this session was already posted to F1Laps
                # But we haven't stored the ID locally (e.g. when user restarts script during a session)
                # We'll try to get the F1Laps ID via GET list call, then try again
                if response.status_code == 400:
                    retrieved_f1_laps_session_id = self.retrieve_f1_laps_session_id(kwargs.get('session_uid'))
                    if retrieved_f1_laps_session_id:
                        f1_laps_session_id = retrieved_f1_laps_session_id
                        # Add session ID to kwargs and update session
                        session_create_params['f1laps_session_id'] = retrieved_f1_laps_session_id
                        success = self.update_session_in_f1laps(**session_create_params)
                    else:
                        log.info("Session can't be created, and no existing session found in F1Laps.")
                else:
                    self._log_f1laps_response_status(response, descriptor="Session_create")
        else:
            # Update session
            success = self.update_session_in_f1laps(**kwargs)
        return success, f1_laps_session_id

    def update_session_in_f1laps(self, **kwargs):
        """ Update existing Session in F1Laps """
        response = self.session_update(**kwargs)
        return response.status_code == 200 if response else False

    def retrieve_f1_laps_session_id(self, session_uid):
        """ Try to retrieve previous session id from F1Laps by listing all sessions """
        list_response = self.session_list(session_uid)
        if list_response is None:
            log.info("API list call failed")
            return None
        list_response_content = json.loads(list_response.content)
        if list_response_content['results'] and len(list_response_content['results']) == 1:
            f1_laps_session_id = list_response_content['results'][0]['id']
            log.info("Found existing session id %s in F1Laps" % f1_laps_session_id)
            return f1_laps_session_id
        else:
            log.info("No session found in F1Laps")
            return None

    def _log_f1laps_response_status(self, response, descriptor):
        if response is None:
            log.info("%s failed, empty response" % descriptor)
        elif response.status_code == 201:
            log.info("%s succeeded" % descriptor)
        elif response.status_code == 400:
            # Log level depends on error type
            error_message = response.content.get('detail')
            if error_message != 'You need an active subscription to use the F1Laps Telemetry App.':
                log.info("%s failed: no active F1Laps subscription" % descriptor)
            else:
                log.error("%s failed: %s" % (descriptor, json.loads(error_message)))
        else:
            log.error("%s failed: %s" % (descriptor, json.loads(response.content)))

    def _get_headers(self):
        return {
            'Content-Type'      : 'application/json',
            'Authorization'     : 'Token %s' % self.api_key,
            'X-F1Laps-App'      : 'F1Laps Telemetry v%s' % self.version,
            'X-F1Laps-Platform' : self._get_platform()
        }

    def _get_platform(self):
        return "%s %s" % (platform.system(), platform.release())
