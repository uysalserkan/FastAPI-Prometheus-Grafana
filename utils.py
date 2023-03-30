"""Utility functions."""

from configparser import ConfigParser


class ConfigParameters:
    """Doldurulacak."""
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ConfigParameters, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, 'config'):
            self.config = ConfigParser()
            self.config.read("config.cfg")

    def get(self, section: str, key: str) -> str:
        """Get key from specific section.

        Parameters:
        -----------
            section `str`: Header section.
            key `str`: Wanted key of value.

        Return:
        -------
            Key `str`
        """
        return self.config.get(section, key)
