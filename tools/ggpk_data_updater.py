"""
Updates the data files. These are extracted from ggpk files using RePOE.
This needs to run whenever POE's ggpk data file is updated with new base items,
item classes, as these are the data items used in Siosa.
Steps-
1. Remove item blacklist from RePOE (base_items.py)
2. Run RePoe (python run_parser.py all)
3. Run this tool with the path to base_items.json as argument
"""
import argparse
import json
import logging
import os
import sys

from siosa.common.util import parent

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()

BASE_ITEMS_FILE_NAME = "base_items.json"
ITEM_CLASSES_FILE_NAME = "item_classes.json"


def get_base_items_file_path(fname):
    siosa_base = parent(parent(__file__))
    return os.path.join(
        siosa_base, "siosa/resources/ggpk_data/{}".format(fname))


def update_base_items(base_items_file_handle):
    data = json.load(base_items_file_handle)
    if not data:
        return False
    output = {
        'data': []
    }
    class_names = set()
    for key, item in data.items():
        output_item = {
            'id': key,
            'Width': item["inventory_width"],
            'Height': item["inventory_height"],
            'Name': item["name"],
            'Class': item["item_class"].replace(" ", ""),
        }
        output['data'].append(output_item)
        class_names.add(output_item["Class"])
    json.dump(
        output, open(get_base_items_file_path(BASE_ITEMS_FILE_NAME), 'w'))
    json.dump(
        {'data': list(class_names)},
        open(get_base_items_file_path(ITEM_CLASSES_FILE_NAME), 'w'))
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Updates ggpk data for Siosa '
                                                 'using RePOE generated json')
    parser.add_argument('base_items_json_path',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help='Path to base_items.json file')

    args = parser.parse_args()
    base_items_file_path = args.base_items_json_path
    success = update_base_items(base_items_file_path)
    if success:
        logger.debug("Successfully updated ggpk data".format())
    else:
        logger.debug("Error: Couldn't update ggpk data")
        sys.exit(1)

