import logging
import time
from enum import Enum

from siosa.common.singleton import Singleton
from siosa.config.siosa_config import SiosaConfig
from siosa.data.poe_item import ItemType
from siosa.data.poe_item_factory import PoeItemFactory
from siosa.network.poe_api import PoeApi


class Stash(metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.config = SiosaConfig().config
        self.poe_api = PoeApi()
        self.name_to_stash_tab = {}
        self.tab_type_to_tabs = {}
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

    def get_stash_tabs_by_name(self, name):
        if name not in self.name_to_stash_tab.keys():
            self.logger.error("Stash tab with name={} is not present in Stash"
                              .format(name))
            return None
        # Return first stash tab incase there are multiple by the same name.
        return self.name_to_stash_tab[name]

    def get_stash_tabs_for_item(self, item):
        stash_tab_type = self._get_stash_type_for_item(item)
        self.logger.info("Stash tab type={} for item_type=({})".format(
            stash_tab_type, item.type))

        if stash_tab_type == StashTabType.CURRENCY:
            return self.get_currency_stash_tabs()
        elif stash_tab_type == StashTabType.UNKNOWN or stash_tab_type not in self.tab_type_to_tabs:
            return self.get_dump_stash_tabs()
        return self.tab_type_to_tabs[stash_tab_type]

    def _populate_internal(self):
        self.tabs = {}
        tabs = sorted(self.stash_metadata['tabs'], key=(lambda x: x['i']))

        for tab in tabs:
            name = tab['n']
            index = tab['i']
            stash_type_str = tab['type']
            is_quad = (stash_type_str == 'QuadStash')
            is_premium = (stash_type_str == 'PremiumStash')
            stash_tab = StashTab({
                'type': stash_type_str,
                'name': name,
                'index': index,
                'is_quad': is_quad,
                'is_premium': is_premium
            })
            self.logger.debug("Creating stash-tab {}".format(str(stash_tab)))
            if name not in self.name_to_stash_tab:
                self.name_to_stash_tab[name] = [stash_tab]
            else:
                self.name_to_stash_tab[name].append(stash_tab)

            stash_type = stash_tab.get_type()
            if stash_type not in self.tab_type_to_tabs:
                # We just take the first stash for each stash type.
                self.tab_type_to_tabs[stash_type] = [stash_tab]
            else:
                self.tab_type_to_tabs[stash_type].append(stash_tab)
            self.tabs[index] = stash_tab

    def get_currency_stash_tabs(self):
        return self._get_all_stashes_with_names(
            self.config['stashes']['currency'])

    def get_dump_stash_tabs(self):
        return self._get_all_stashes_with_names(self.config['stashes']['dump'])

    def _get_all_stashes_with_names(self, tab_names):
        stash_tabs = []
        for name in tab_names:
            stash_tabs.extend(self.get_stash_tabs_by_name(name))
        return stash_tabs
        
    def _get_stash_type_for_item(self, item):
        if item.type == ItemType.CURRENCY:
            return StashTabType.CURRENCY
        elif item.type == ItemType.DIVINATION_CARD:
            return StashTabType.DIVINATION
        elif item.type in (ItemType.DELIRIUM_ORB,
                           ItemType.SIMULACRUM_SPLINTER,
                           ItemType.SIMULACRUM):
            return StashTabType.DELIRIUM
        elif item.type in (ItemType.CATALYST, ItemType.ORGAN):
            return StashTabType.METAMORPH
        elif item.type == ItemType.OIL:
            return StashTabType.BLIGHT
        elif item.type in (ItemType.DELVE_RESONATOR, ItemType.DELVE_FOSSIL):
            return StashTabType.DELVE
        elif item.type in (ItemType.SPLINTER,
                           ItemType.SCARAB,
                           ItemType.FRAGMENT,
                           ItemType.OFFERING,
                           ItemType.DIVINE_VESSEL,
                           ItemType.TIMELESS_EMBLEM,
                           ItemType.BREACHSTONE):
            return StashTabType.FRAGMENT
        elif item.type == ItemType.ESSENCE:
            return StashTabType.ESSENCE
        elif item.type == ItemType.MAP:
            return StashTabType.MAP
        else:
            return StashTabType.UNKNOWN


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
        self.index = int(data['index'])
        self.name = data['name']
        self.is_quad = bool(data['is_quad'])
        self.is_premium = bool(data['is_premium'])
        self.item_factory = PoeItemFactory()
        self.last_fetched_ts = 0

        self.contents = []
        self.items = {}

    def get_type(self):
        for t in StashTabType:
            if t.value == self.type:
                return t
        return StashTabType.UNKNOWN

    def get_item_at_location(self, x, y):
        item = self._get_item(x, y)
        if item:
            return item
        items = self._get_contents()
        for item in items:
            if item['x'] == x and item['y'] == y:
                self.items[(x, y)] = self.item_factory.get_item(
                    item, source='stash')
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
