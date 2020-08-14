import logging
from enum import Enum

from siosa.common.decorations import singleton


@singleton
class Stash:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.poe_api = PoeApi.get_instance()
        self.name_to_stash_tab = {}
        self.index_to_stash_tab = {}
        self.tabs = {}
        self.stash_metadata = None
        self.refresh()

    def refresh(self):
        self.logger.info("Refreshing stash data.")
        self.stash_metadata = self.poe_api.get_stash_metadata()
        self._populate_internal()

    def get_stash_tab_contents(self, index):
        if index not in self.index_to_stash_tab.keys():
            return {}
        self.logger.info("Getting stash contents for stash {}".format(
            self.index_to_stash_tab[index].name))
        self.tabs[index].set_contents(self.poe_api.get_stash_contents(index))
        return self.tabs[index].get_contents()

    def get_stash_index_for_name(self, name):
        if name in self.name_to_stash_tab.keys():
            return self.name_to_stash_tab[name].index
        return None

    def _populate_internal(self):
        self.tabs = {}
        for tab in self.stash_metadata['tabs']:
            name = tab['n']
            index = tab['i']
            is_quad = (tab['type'] == 'QuadStash')
            is_premium = (tab['type'] == 'PremiumStash')
            stash_tab = StashTab({
                'name': name,
                'index': index,
                'is_quad': is_quad,
                'is_premium': is_premium
            })
            self.name_to_stash_tab[name] = stash_tab
            self.index_to_stash_tab[index] = stash_tab
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
    def __init__(self, data):
        self.api = PoeApi.get_instance()
        self.type = data['type']
        self.index = data['index']
        self.name = data['name']
        self.is_quad = data['is_quad']
        self.is_premium = data['is_premium']

    def get_type(self):
        for t in StashTabType:
            if t.value == self.type:
                return t.name
        return StashTabType.UNKNOWN
    
    def set_contents(self, contents):
        self.contents = contents
        
    def get_contents(self):
        return self.contents