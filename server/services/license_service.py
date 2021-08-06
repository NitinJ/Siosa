from license.license import License
from siosa.config.siosa_config import SiosaConfig


class LicenseService:
    def __init__(self, siosa_config: SiosaConfig):
        self.config = siosa_config

    def get(self):
        return {
            "key": self.config.get_license_key(),
            "valid": License.valid(self.config.get_license_key())
        }

    def register(self, key):
        valid = License.register(key)
        if valid:
            self.config.update({"license_key": key})
        return {
            "key": key,
            "valid": valid
        }
