import ConfigParser
import os


class Configuration(object):
    def __init__(self):
        self.config_dir = os.path.expanduser('~/.config/hollande')
        self.config_file = os.path.join(self.config_dir, '.holland.cfg')
        self._load_settings()

    def _load_settings(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, 0700)

        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)

    def get(self, section, option, *args, **kwargs):
        return self.config.get(section, option, *args, **kwargs)

    def set(self, section, option, *args, **kwargs):
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, option, *args, **kwargs)

        with open(self.config_file, 'wb') as config_file:
            self.config.write(config_file)
