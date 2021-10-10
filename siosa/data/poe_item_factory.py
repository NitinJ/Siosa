from siosa.clipboard.clipboard_reader import ClipboardReader
from siosa.data.clipboard_item_factory import ClipboardItemFactory
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.stash_item_factory import StashItemFactory
from siosa.network.poe_api import PoeApi


class PoeItemFactory:
    def __init__(self):
        self.cif_ = ClipboardItemFactory()
        self.sif_ = StashItemFactory()

    def get_item(self, data, source='clipboard'):
        """
        Args:
            data:
            source:
        """
        if source == 'clipboard':
            return self.cif_.get_item(data)
        return self.sif_.get_item(data)


if __name__ == "__main__":
    exchange = CurrencyExchange(
        PoeApi("MopedDriverr", "0dfdc62a6d647095161d19e802961ef3",
               "Expedition"))
    data = ClipboardReader().get_clipboard_data()
    factory = PoeItemFactory()
    item = factory.get_item(data)
    print(item)
    print(item.get_trade_name())