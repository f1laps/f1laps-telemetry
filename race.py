from receiver.receiver import RaceReceiver
from receiver.helpers import asciiart

import config


if __name__ == '__main__':
    asciiart()
    # Initiative receiver
    race_receiver = RaceReceiver(f1laps_api_key=config.F1LAPS_API_KEY, run_as_daemon=False)
    # Listen to packages
    race_receiver.start()
