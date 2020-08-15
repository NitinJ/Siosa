from siosa.data.clipboard_item_factory import ClipboardItemFactory
from siosa.data.stash_item_factory import StashItemFactory


class PoeItemFactory:
    def __init__(self):
        self.cif_ = ClipboardItemFactory()
        self.sif_ = StashItemFactory()

    def get_item(self, data, source='clipboard'):
        if source == 'clipboard':
            return self.cif_.get_item(data)
        return self.sif_.get_item(data)
