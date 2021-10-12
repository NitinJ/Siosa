from siosa.data.poe_item import Item, ItemType
from siosa.data.stash import StashTab, Stash


class StashItem(Item):
    def __init__(self,
                 item_info,
                 affixes,
                 stash_tab: StashTab, position, item_type=ItemType.UNKNOWN):
        """
        Args:
            item_info:
            affixes:
            stash_tab (StashTab):
            position:
            item_type:
        """
        Item.__init__(self, item_info, affixes, item_type=item_type)
        self.stash_tab = stash_tab
        self.position = position

        # The right stash tab for this item. For eg. a chaos orb should be in
        # the currency tab if tab is available.
        self.correct_stash_tab = None

        tabs = Stash().get_stash_tabs_for_item(self)
        if not tabs or not len(tabs):
            self.correct_stash_tab = tabs[0]

    @staticmethod
    def create_from(item, stash_tab: StashTab, position):
        if not item or not stash_tab or not position:
            return None
        return StashItem(
            item.item_info,
            item.affixes, stash_tab, position, item_type=item.type)
