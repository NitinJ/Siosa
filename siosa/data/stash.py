import logging

from siosa.common.singleton import Singleton
from siosa.config.siosa_config import SiosaConfig
from siosa.data.poe_item import ItemType
from siosa.data.stash_tab import StashTabType, StashTab
from siosa.network.poe_api import PoeApi


def _get_stash_type_for_item(item):
    if not item:
        return StashTabType.UNKNOWN
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


class Stash(metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.config = SiosaConfig().config
        self.poe_api = PoeApi()
        self.name_to_stash_tabs = {}
        self.tab_type_to_tabs = {}
        self.tabs = {}
        self.stash_metadata = None
        self.refresh()

    def refresh(self):
        self.logger.info("Refreshing stash data.")
        self.stash_metadata = self.poe_api.get_stash_metadata()
        self._populate_internal()

    def get_stash_tab_by_index(self, index):
        """
        Returns the stash tab at a given index.
        Args:
            index: Index of stash tab to return

        Returns: Stash tab

        """
        if index not in self.tabs.keys():
            self.logger.error("Invalid stash tab index={}".format(index))
            return None
        return self.tabs[index]

    def get_stash_tabs_by_name(self, name):
        """
        Returns all stash tabs with a given name
        Args:
            name: Name of the stash tabs
        """
        if name not in self.name_to_stash_tabs.keys():
            self.logger.error("Stash tab with name={} is not present in Stash"
                              .format(name))
            return None
        return self.name_to_stash_tabs[name]

    def get_stash_tabs_for_item(self, item):
        """
        Returns a list of stash tabs to which the given item belongs.
        Args:
            item: Item
        """
        stash_tab_type = _get_stash_type_for_item(item)
        self.logger.info("Stash tab type={} for item_type=({})".format(
            stash_tab_type, item.type))

        if stash_tab_type == StashTabType.CURRENCY:
            return self.get_currency_stash_tabs()
        elif stash_tab_type == StashTabType.UNKNOWN or \
                stash_tab_type not in self.tab_type_to_tabs:
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
            if name not in self.name_to_stash_tabs:
                self.name_to_stash_tabs[name] = [stash_tab]
            else:
                self.name_to_stash_tabs[name].append(stash_tab)

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
        for tab_name in tab_names:
            stash_tabs.extend(self.get_stash_tabs_by_name(tab_name))
        return stash_tabs
