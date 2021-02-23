# F1Laps Telemetry Sync
![unittests](https://github.com/f1laps/f1laps-telemetry/actions/workflows/python-test.yml/badge.svg)

This package lets you sync F1 game data into [F1Laps](https://www.f1laps.com) automatically. It receives telemetry packets via the UDP protocol in your local network.

## Requirements

* Python 3
* Package requirements (see requirements.txt)

## Installation & Usage

Please check out our comprehensive documentation here:

**[F1Laps Telemetry Sync User Documentation](https://www.notion.so/F1Laps-Telemetry-Documentation-55ad605471624066aa67bdd45543eaf7)**

## Configuration

Set your F1Laps API key in the config.py. You can get your API key from [https://www.f1laps.com/api/telemetry_apps](https://www.f1laps.com/api/telemetry_apps).
```python
F1LAPS_API_KEY = "YOUR_API_KEY"
```

Once you start the script, it will show the IP and port it's receiving packages on, like so:
```bash
2021-02-19 19:34:42   Set your F1 game telemetry IP to:   192.168.4.20
2021-02-19 19:34:42   Set your F1 game telemetry port to: 20777
```

In your F1 game settings (Settings > Telemetry), change the IP and port accordingly.

## Testing
You can run all unit tests with this command:
```bash
python3 -m unittest discover
```

## Credits & Contributions
This repository was heavily inspired and contributed to by:
* [Redditor _jsplit](https://www.reddit.com/user/_jsplit)
* [gparent's f1-2020-telemetry package](https://gitlab.com/gparent/f1-2020-telemetry/)
