from lib.logger import log


class ConfigFile:
    """ Read / write config file """

    def __init__(self):
        self.api_key  = None
        self.api_key_field_name = "API_KEY"
        self.config_file_name = "lib/file_session.txt"

    def write(self, value):
        f = open(self.config_file_name, "w") 
        api_key_config_text = "%s=%s" % (self.api_key_field_name, value)
        with open(self.config_file_name, 'w') as f: 
            f.write(api_key_config_text)

    def read(self):
        f = open(self.config_file_name, "r") 
        file_content = f.read()
        f.close()
        return file_content

    def get_api_key(self):
        file_content = self.read()
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
        self.write(self.api_key)
        log.debug("Saved API key in config file")
        
