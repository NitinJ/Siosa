import json
import logging
import subprocess

import requests

from siosa.config.siosa_config import SiosaConfig

MID_PROC = "wmic csproduct get uuid"
SERVER = "https://siosa-poe.com"
REGISTER = "/api/v1/licenses/register"
VERIFY = "/api/v1/licenses/verify"


def _get_muid():
    try:
        return \
            subprocess.check_output(MID_PROC).decode().split('\n')[1].strip()
    except:
        return None


class License:
    def __init__(self, siosa_config: SiosaConfig):
        """
        Args:
            siosa_config (SiosaConfig):
        """
        self.config = siosa_config
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def valid(self, _key=None):
        self.logger.debug("Validating license")
        key = self.config.get_license_key() if not _key else _key
        if not key:
            self.logger.info("License key not set !")
            return False

        muid = _get_muid()
        if not muid:
            return False

        resp = requests.post(SERVER + VERIFY,
                             json={'license_key': key, "muid": muid})
        if resp:
            return True
        return False

    def register(self, key):
        """

        Args:
            key: The new key to register.

        Returns: Whether the operation succeeded.

        """
        if not key:
            return False

        muid = _get_muid()
        if not muid:
            return False

        resp = requests.post(SERVER + REGISTER,
                             json={'license_key': key, "muid": muid})

        if resp:
            self.config.set_license_key(key)
            return True
        return False
