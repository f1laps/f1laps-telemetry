#!/usr/bin/env python3
import logging


LOG_LEVEL  = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)-8s - %(message)s"

# create main logger
logging.basicConfig(
    level    = LOG_LEVEL,
    format   = LOG_FORMAT,
    handlers = [
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# disable logging of modules
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3" ).setLevel(logging.WARNING)