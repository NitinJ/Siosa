import json
import os


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
        return os.path.join(os.path.dirname(__file__), filename)

    @staticmethod
    def get_item_dimensions(item_name):
        """
        Args:
            item_name:
        """
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
            BaseItems._items[v['name']] = {
                'inventory_height' : v['inventory_height'],
                'inventory_width' : v['inventory_width']
            }
