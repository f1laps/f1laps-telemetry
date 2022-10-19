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
    supported_config_names = ["API_KEY", "UDP_BROADCAST_ENABLED", "IP_VALUE", "PORT_VALUE", "UDP_REDIRECT_ENABLED",
                              "REDIRECT_HOST_VALUE", "REDIRECT_PORT_VALUE"]
    config_file_name = "f1laps_configuration.txt"

    def __init__(self):
        self.config = {}

    def get(self, field_name):
        if field_name not in self.supported_config_names:
            raise Exception("Field name %s not supported in config" % field_name)
        if self.config and field_name in self.config.keys():
            value = self.config.get(field_name)
            return self._map_string_to_bool(self._clean_string(value))

    def set(self, field_name, field_value):
        if field_name not in self.supported_config_names:
            raise Exception("Field name %s not supported in config" % field_name)
        field_value = self._map_bool_to_string(self._clean_string(field_value))
        self.config[field_name] = field_value
        self._write_config()

    def load(self):
        file_lines = self._read_config()
        if not file_lines:
            return self
        for line in file_lines:
            try:
                line_name, line_value = line.split("=")
                if line_name in self.supported_config_names:
                    self.config[line_name] = line_value.rstrip()
            except Exception as ex:
                log.info("Could not read line from readlines (%s)" % ex)
        return self

    def _clean_string(self, value):
        if value in ["", "None"]:
            return None
        return value

    def _map_bool_to_string(self, value):
        if value == True:
            return "1"
        elif value == False:
            return "0"
        return value

    def _map_string_to_bool(self, value):
        if value == "1":
            return True
        elif value == "0":
            return False
        return value

    def _write_config(self):
        file_lines = []
        for key, value in self.config.items():
            file_lines.append("%s=%s" % (key, value))
        if not file_lines:
            return
        try:
            with open(get_path_executable_parent(self.config_file_name), 'w+') as f:
                f.writelines("%s\n" % l for l in file_lines)
        except Exception as ex:
            log.debug("Could not write to config file: %s" % ex)

    def _read_config(self):
        try:
            f = open(get_path_executable_parent(self.config_file_name), "r")
            file_content = f.readlines()
            f.close()
            return file_content
        except Exception as ex:
            log.debug("Could not read config file (%s)" % ex)
            return None
