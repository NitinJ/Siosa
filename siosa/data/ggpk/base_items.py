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
    def get_item_dimensions(item_name):
        """
        Args:
            item_name:
        """
        item_name = item_name.strip().lower()
        if not BaseItems._items:
            BaseItems._preprocess()
        if item_name not in BaseItems._items.keys():
            return None
        data = BaseItems._items[item_name]
        return data['inventory_width'], data['inventory_height']

    @staticmethod
    def _preprocess():
        data = json.load(open(BaseItems._get_path(BaseItems.FILE_NAME), 'r'))
        for k,v in data.items():
            if "Metadata" not in k:
                continue
            BaseItems._items[v['name'].lower()] = {
                'inventory_height' : v['inventory_height'],
                'inventory_width' : v['inventory_width']
            }


if __name__ == "__main__":
    print(BaseItems.get_item_dimensions("Contract: Tunnels"))