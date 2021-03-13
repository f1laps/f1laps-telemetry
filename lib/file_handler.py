from os import path
import sys

from lib.logger import log


def get_path_executable_parent(file_name):
    """ 
    Get the path of the executable's enclosing folder
    Used to create the config file next to the exe
    """
    bundle_dir = None
    try:
        if getattr(sys, 'frozen'):
            bundle_dir = sys.executable
    except Exception as ex:
        log.debug("Could not find sys.frozen or sys.executable (%s)" % ex)
    if not bundle_dir:
        bundle_dir = path.abspath(path.dirname(__file__))
    path_to_file = path.abspath(path.join(path.dirname(bundle_dir), file_name))
    return path_to_file


def get_path_temporary(file_name):
    """ 
    Get the path of the temporary folder created by bundled exes
    Used to retrive image files, like the F1Laps logo
    """
    bundle_dir = None
    try:
        if getattr(sys, 'frozen'):
            bundle_dir = sys._MEIPASS
    except Exception as ex:
        log.debug("Could not find sys._MEIPASS (%s)" % ex)
    if not bundle_dir:
        bundle_dir = path.abspath(path.dirname(path.dirname(__file__)))
    path_to_file = path.abspath(path.join(bundle_dir, file_name))
    return path_to_file


class ConfigFile:
    """ Read / write config file """

    def __init__(self):
        self.api_key  = None
        self.api_key_field_name = "API_KEY"
        self.config_file_name = "f1laps_configuration.txt"

    def get_api_key(self):
        file_content = self._read()
        if file_content:
            try:
                api_key_field_name, api_key = file_content.split("=")
                self.api_key = api_key
                return api_key
            except Exception as ex:
                log.debug("Could not read API key from file (%s)" % ex)
        else:
            log.debug("Config file is empty")
        return None

    def set_api_key(self, api_key):
        self.api_key = api_key
        self._write(self.api_key)
        log.debug("Saved API key in config file")

    def _write(self, value):
        api_key_config_text = "%s=%s" % (self.api_key_field_name, value)
        try:
            with open(get_path_executable_parent(self.config_file_name), 'w+') as f: 
                f.write(api_key_config_text)
        except Exception as ex:
            log.debug("Could not write to config file: %s" % ex)

    def _read(self):
        try:
            f = open(get_path_executable_parent(self.config_file_name), "r") 
            file_content = f.read()
            f.close()
            return file_content
        except Exception as ex:
            log.debug("Could not read config file (%s)" % ex)
            return None
        
