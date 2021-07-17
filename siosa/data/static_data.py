from siosa.common.singleton import Singleton
from siosa.network.poe_api import PoeApi


class StaticData(metaclass=Singleton):
    def __init__(self):
        self.poe_api = PoeApi()
        self.name_to_id = {}
        self.currency_data = None

    def get_trade_id_for_name(self, name):
        """Returns the trade id for a given trade name. eg- Chaos Orb -> chaos.

        Args:
            name (string): Name of the item
        """
        self._get_static_currency_data()
        if name in self.name_to_id:
            return self.name_to_id[name]
        return None

    def get_name_for_trade_id(self, id):
        """Returns the name for a given trade id for an item

        Args:
            id (string): Trade id of the item
        """
        self._get_static_currency_data()
        for name, t_id in self.name_to_id.items():
            if t_id == id:
                return name
        return None

    def _get_static_currency_data(self):
        if self.currency_data:
            return self.currency_data
        data = self.poe_api.get_static_data()
        self._parse_static_currency_data(data)
        self.currency_data = data

    def _parse_static_currency_data(self, data):
        """
        Args:
            data:
        """
        for entry_type in data:
            for entry in entry_type['entries']:
                self.name_to_id[entry['text']] = entry['id']
