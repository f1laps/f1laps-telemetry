from PyQt5.QtCore import QObject, pyqtSignal
from lib.logger import log
import requests
import json

F1LAPS_USER_SETTINGS_ENDPOINT = "https://www.f1laps.com/api/f12020/telemetry/app/user/settings/"


class APIUserPreferenceWorker(QObject):
    user_settings = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def run(self):
        """ Return if user is authenticated and supports telemetry 
        (user_is_valid, user_telemetry_enabled)"""
        user_settings_dict = {
            "api_key_valid": False,
            "telemetry_enabled": False,
            "subscription_plan": None,
            "subscription_expires": None
        }
        try:
            headers = {'Authorization': 'Token %s' % self.api_key,}
            response = requests.get(F1LAPS_USER_SETTINGS_ENDPOINT, headers=headers)
            if response.status_code == 401:
                log.info("API key %s is invalid" % self.api_key)
                self.user_settings.emit(user_settings_dict)
            elif response.status_code == 200:
                json_response = json.loads(response.content)
                telemetry_enabled = json_response.get('telemetry_enabled')
                subscription_plan = json_response.get('subscription_plan')
                subscription_expires = json_response.get('subscription_expires')
                log.info("Authenticated against F1Laps API successfully. Telemetry is %s" % \
                    ("enabled" if telemetry_enabled else "not enabled"))
                user_settings_dict["api_key_valid"] = True
                user_settings_dict["telemetry_enabled"] = telemetry_enabled
                user_settings_dict["subscription_plan"] = subscription_plan
                user_settings_dict["subscription_expires"] = subscription_expires
                self.user_settings.emit(user_settings_dict)
            else:
                log.warning("Received invalid F1Laps status code %s" % response.status_code)
                self.user_settings.emit(user_settings_dict)
        except Exception as ex:
            log.warning("Couldn't get user settings from F1Laps due to: %s" % ex)
            self.user_settings.emit(user_settings_dict)
        self.finished.emit()