from f1laps_telemetry_2020.receiver import RaceReceiver
from f1laps_telemetry_2020.helpers import asciiart

import config


if __name__ == '__main__':
    asciiart()
    # Initiative receiver
    race_receiver = RaceReceiver(config.F1LAPS_API_KEY)
    # Listen to packages
    race_receiver.start()
