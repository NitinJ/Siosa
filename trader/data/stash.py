import logging

from common.decorations import singleton

@singleton
class Stash:
    def __init__(self, poe_api):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.name_to_info = {}
        self.index_to_name = {}
        self.contents = {}
        self.poe_api = poe_api
        self.stash_metadata = None

        self.refresh()

    def refresh(self):
        self.logger.info("Refreshing stash data.")
        self.stash_metadata = self.poe_api.get_stash_metadata()
        self.contents = {}
        self._populate_internal()

    def get_stash_contents(self, index):
        if index not in self.index_to_name.keys():
            return {}
        self.logger.info("Getting stash contents for stash {}".format(self.index_to_name[index]))
        self.contents[index] = self.poe_api.get_stash_contents(index)
        return self.contents[index]

    def get_stash_index_for_name(self, name):
        if name in self.name_to_info.keys():
            return self.name_to_info[name]['index']
        return None

    def _populate_internal(self):
        for tab in self.stash_metadata['tabs']:
            name = tab['n']
            index = tab['i']
            is_quad = (tab['type'] == 'QuadStash')
            is_premium = (tab['type'] == 'PremiumStash')
            self.name_to_info[name] = {
                'index': index,
                'is_quad': is_quad,
                'is_premium': is_premium
            }
            self.index_to_name[index] = name
