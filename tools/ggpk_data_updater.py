import json
import logging
import os
import sys

import requests

from siosa.common.util import parent

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger()

VERSION_URL = "https://poedat.erosson.org/pypoe/v1/latest.json"
BASE_ITEMS_URL = "https://poedat.erosson.org/pypoe/v1/tree/{version}/default/BaseItemTypes.dat.min.json"


def get_base_items_file_path():
    siosa_base = parent(parent(__file__))
    return os.path.join(
        siosa_base, "siosa/resources/ggpk_data/base_items.json")


def get_latest_version():
    resp = requests.get(VERSION_URL)
    if not resp.content:
        return None
    data = json.loads(resp.content)
    if not data or 'version' not in data:
        return None
    return data['version']


def get_current_version():
    file_path = get_base_items_file_path()
    if not os.path.exists(file_path):
        return None
    data = json.load(open(file_path, 'r'))
    if not data or 'version' not in data:
        return None
    return data['version']


def fetch_and_update_base_items(version):
    url = BASE_ITEMS_URL.format(version=version)
    resp = requests.get(url)
    if not resp or not resp.content:
        return False
    data = json.loads(resp.content)
    if not data or 'data' not in data:
        return False
    output = {
        'version': version,
        'filename': data['filename'],
        'data': []
    }
    for item in data['data']:
        output_item = {
            'id': item[0],
            'Width': item[2],
            'Height': item[3],
            'Name': item[4],
            'Class': item[5]
        }
        output['data'].append(output_item)
    json.dump(output, open(get_base_items_file_path(), 'w'))
    return True


if __name__ == "__main__":
    latest_version = get_latest_version()
    if not latest_version:
        logger.error("Couldn't get latest version from {}".format(VERSION_URL))
        sys.exit(1)

    current_version = get_current_version()
    if latest_version == current_version:
        logger.debug("Already at latest version !")
        sys.exit(0)

    success = fetch_and_update_base_items(latest_version)
    if success:
        logger.debug("Successfully updated to version: {}".format(
            latest_version))
    else:
        logger.debug(
            "Error: Couldn't update to version: {}".format(latest_version))
