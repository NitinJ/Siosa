import logging
import subprocess

import requests

MID_PROC = "C:\Windows\System32\wbem\WMIC.exe csproduct get uuid"
SERVER = "https://siosa-poe.com"
REGISTER = "/api/v1/licenses/register"
VERIFY = "/api/v1/licenses/verify"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _get_muid():
    try:
        return subprocess.check_output(
            MID_PROC,
            shell=True,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE).decode().split('\n')[1].strip()
    except Exception as e:
        return None


class License:
    @staticmethod
    def valid(key):
        logger.debug("Validating license")
        if not key:
            logger.info("License key not set !")
            return False

        muid = _get_muid()
        if not muid:
            logger.debug("MUID is none")
            return False

        resp = requests.post(SERVER + VERIFY,
                             json={'license_key': key, "muid": muid})
        if resp:
            return True
        return False

    @staticmethod
    def register(key):
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
            return True
        return False


if __name__ == "__main__":
    print(License.valid('2ffab37b-4eb5-479f-a977-71489dffc20e'))
