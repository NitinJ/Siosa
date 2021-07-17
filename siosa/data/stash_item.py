from siosa.data.stash import StashTab


class StashItem:
    def __init__(self, item, stash_tab: StashTab, position):
        """
        Args:
            item:
            stash_tab (StashTab):
            position:
        """
        self.item = item
        self.stash_tab = stash_tab
        self.position = position
