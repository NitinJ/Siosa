from license.license import License
from siosa.config.siosa_config import SiosaConfig


class LicenseService:
    def __init__(self, siosa_config: SiosaConfig):
        self.config = siosa_config
        self.license = License(self.config)

    def get(self):
        return {
            "key": self.config.get_license_key(),
            "valid": self.license.valid()
        }

    def register(self, key):
        return {
            "key": key,
            "valid": self.license.register(key)
        }
