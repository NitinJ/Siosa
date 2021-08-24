import json
import os

from siosa.common.util import parent


class BaseItems:
    """Resource file with metadata for all base items. Sample entry:"""
    _items = {}
    FILE_NAME = "base_items.json"

    @staticmethod
    def _get_path(filename):
        """
        Args:
            filename:
        """
        siosa_base = parent(parent(parent(__file__)))
        return os.path.join(siosa_base, "resources/ggpk_data/{}".format(filename))

    @staticmethod
    def get(item_name):
        if not BaseItems._items:
            BaseItems._preprocess()

        item_name = item_name.strip().lower()
        if item_name not in BaseItems._items.keys():
            return None
        return BaseItems._items[item_name]

    @staticmethod
    def _preprocess():
        data = json.load(open(BaseItems._get_path(BaseItems.FILE_NAME), 'r'))
        for v in data['data']:
            BaseItems._items[v['Name'].lower()] = {
                'inventory_height': v['Height'],
                'inventory_width': v['Width'],
                'item_class': v['Class'].split("/")[-1]
            }


if __name__ == "__main__":
    print(BaseItems.get("Contract: Tunnels"))