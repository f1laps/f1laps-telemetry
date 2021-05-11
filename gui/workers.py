from PyQt5.QtCore import QObject, pyqtSignal


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
            "telemetry_enabled": False
        }
        try:
            headers = {'Authorization': 'Token %s' % self.api_key,}
            response = requests.get(F1LAPS_USER_SETTINGS_ENDPOINT, headers=headers)
            if response.status_code == 401:
                log.info("API key %s is invalid" % self.api_key)
                self.user_settings.emit(user_settings_dict)
            elif response.status_code == 200:
                telemetry_enabled = json.loads(response.content).get('telemetry_enabled')
                log.info("Authenticated successfully. Telemetry is %s" % \
                    ("enabled" if telemetry_enabled else "not enabled"))
                user_settings_dict["api_key_valid"] = True
                user_settings_dict["telemetry_enabled"] = telemetry_enabled
                self.user_settings.emit(user_settings_dict)
            else:
                log.warning("Received invalid F1Laps status code %s" % response.status_code)
                self.user_settings.emit(user_settings_dict)
        except Exception as ex:
            log.warning("Couldn't get user settings from F1Laps due to: %s" % ex)
            self.user_settings.emit(user_settings_dict)
        self.finished.emit()