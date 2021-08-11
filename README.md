# F1Laps Telemetry Sync
![unittests](https://github.com/f1laps/f1laps-telemetry/actions/workflows/python-test.yml/badge.svg)

This package lets you sync F1 game data into [F1Laps](https://www.f1laps.com) automatically. It receives telemetry packets via the UDP protocol in your local network.

## Requirements & Installation

* Python 3
* Package requirements, see requirements.txt

## Testing

You can run all unit tests with this command:
```bash
python3 -m unittest discover
```

## Desktop Apps

You can build Mac and Windows apps via PyInstaller, which offer a graphical user interface for running this script.

**Mac** 

```bash
# First one returns GUI app; second one returns GUI+console exe
python3 -m PyInstaller app.py --noconsole --name F1Laps --icon images/app-icon.icns --add-data 'logo.svg:.'
python3 -m PyInstaller app.py --onefile --name F1Laps --icon images/app-icon.icns --add-data 'logo.svg:.'
```

**Windows** 

```bash
# First one returns GUI exe; second one returns GUI+console exe
pyinstaller app.py --onefile --noconsole --name F1Laps --icon images/app-icon.ico --add-data "logo.svg;."
pyinstaller app.py --onefile --name F1Laps --icon images/app-icon.ico --add-data "logo.svg;."
```

## Credits & Contributions

This repository was heavily inspired and contributed to by:
* [Redditor _jsplit](https://www.reddit.com/user/_jsplit)
* [gparent's f1-2020-telemetry package](https://gitlab.com/gparent/f1-2020-telemetry/)
