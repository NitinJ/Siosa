import logging
from enum import Enum
import time

from siosa.common.decorations import singleton
from siosa.network.poe_api import PoeApi
from siosa.data.poe_item_factory import PoeItemFactory


@singleton
class Stash:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.poe_api = PoeApi()
        self.name_to_stash_tab = {}
        self.tabs = {}
        self.stash_metadata = None
        self.refresh()

    def refresh(self):
        self.logger.info("Refreshing stash data.")
        self.stash_metadata = self.poe_api.get_stash_metadata()
        self._populate_internal()

    def get_stash_tab_by_index(self, index):
        if index not in self.tabs.keys():
            self.logger.error("Invalid stash tab index={}".format(index))
            return None
        return self.tabs[index]

    def get_stash_tab_by_name(self, name):
        if name not in self.name_to_stash_tab.keys():
            self.logger.error("Stash tab with name={} is not present in Stash"
                              .format(name))
            return None
        return self.name_to_stash_tab[name]
    
    def _populate_internal(self):
        self.tabs = {}
        for tab in self.stash_metadata['tabs']:
            name = tab['n']
            index = tab['i']
            stash_type = tab['type']
            is_quad = (stash_type == 'QuadStash')
            is_premium = (stash_type == 'PremiumStash')
            stash_tab = StashTab({
                'type': stash_type,
                'name': name,
                'index': index,
                'is_quad': is_quad,
                'is_premium': is_premium
            })
            self.logger.debug("Creating stash-tab {}".format(str(stash_tab)))
            self.name_to_stash_tab[name] = stash_tab
            self.tabs[index] = stash_tab


class StashTabType(Enum):
    UNKNOWN = 'Unknown'
    CURRENCY = 'CurrencyStash'
    MAP = 'MapStash'
    ESSENCE = 'EssenceStash'
    DIVINATION = 'DivinationCardStash'
    FRAGMENT = 'FragmentStash'
    UNIQUE = 'UniqueStash'
    METAMORPH = 'MetamorphStash'
    BLIGHT = 'BlightStash'
    DELVE = 'DelveStash'
    DELIRIUM = 'DeliriumStash'


class StashTab:
    REFRESH_DURATION = 5*60  # 5 mins

    def __init__(self, data):
        self.api = PoeApi()
        self.type = data['type']
        self.index = data['index']
        self.name = data['name']
        self.is_quad = data['is_quad']
        self.is_premium = data['is_premium']
        self.item_factory = PoeItemFactory()
        self.last_fetched_ts = 0

        self.contents = []
        self.items = {}

    def get_type(self):
        for t in StashTabType:
            if t.value == self.type:
                return t.name
        return StashTabType.UNKNOWN

    def get_item_at_location(self, x, y):
        item = self._get_item(x, y)
        if item:
            return item
        items = self._get_contents()
        for item in items:
            if item['x'] == x and item['y'] == y:
                self.items[(x, y)] = self.item_factory.get_item(item, source='stash')
                return self.items[(x, y)]
        return None

    def _get_contents(self):
        if time.time() - self.last_fetched_ts > StashTab.REFRESH_DURATION:
            self._refresh_data()
        return self.contents
    
    def _refresh_data(self):
        self.contents = self.api.get_stash_contents(self.index)
        self.items = {}
        self.last_fetched_ts = time.time()

    def _get_item(self, x, y):
        if (x, y) in self.items.keys():
            return self.items[(x, y)]
        return None

    def __str__(self):
        return "type: {}, index: {}, name: {}, quad: {}, premium: {}".format(
            self.type,
            self.index,
            self.name,
            self.is_quad,
            self.is_premium)
