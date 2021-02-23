import logging

LOG_LEVEL = "DEBUG"

# create main logger
logging.basicConfig(format='%(asctime)s - %(levelname)-8s - %(message)s')
log = logging.getLogger(__name__)

# set log level
log_level = logging.getLevelName(LOG_LEVEL)
log.setLevel(log_level)

# disable logging of modules
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)