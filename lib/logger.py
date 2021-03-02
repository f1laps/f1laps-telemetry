#!/usr/bin/env python3
import logging
import sys
from os import path
from logging.handlers import TimedRotatingFileHandler


def get_path():
    FILENAME = 'f1laps_telemetry_logs.txt'
    if getattr(sys, 'frozen', False):
        application_path = sys.executable 
    else:
        application_path = path.abspath(path.join(path.dirname(path.dirname(__file__)), FILENAME))
    return application_path


LOG_LEVEL             = "INFO"
LOG_FORMAT            = "%(asctime)s - %(levelname)-8s - %(message)s"
LOG_FILE_PATH         = get_path()
LOG_FILE_ROTATE       = "midnight"
LOG_FILE_BACKUP_COUNT = 7

# create main logger
logging.basicConfig(
    level    = LOG_LEVEL,
    format   = LOG_FORMAT,
    handlers = [
        TimedRotatingFileHandler(LOG_FILE_PATH, 
                                 when     = LOG_FILE_ROTATE,
                                 interval = LOG_FILE_BACKUP_COUNT),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# disable logging of modules
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3" ).setLevel(logging.WARNING)