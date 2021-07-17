import logging

from siosa.config.siosa_config import SiosaConfig


class License:
    def __init__(self, siosa_config: SiosaConfig):
        """
        Args:
            siosa_config (SiosaConfig):
        """
        self.config = siosa_config
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def valid(self):
        self.logger.debug("Validating license")
        key = self.config.get_license_key()
        if not key:
            self.logger.info("License key not set !")
            return False
        # TODO: Call license server and check validity
        return True