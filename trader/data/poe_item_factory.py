import logging

from clipboard.clipboard_util import *
from poe_item import ItemType
from poe_currencies import *

# Creates poe items from poe clipboard data.
class PoeItemFactory:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

    def get_item(self, clipboard_data):
        if not clipboard_data or clipboard_data.find(LINE_FEED) == -1:
            return None
        self.logger.debug("Getting item from clipboard data")
        
        type = get_clipboard_item_type(clipboard_data)
        self.logger.debug("Got {} from clipboard".format(type))
        
        if type == ItemType.CURRENCY:
            return self._create_currency_item(clipboard_data)
        elif type == ItemType.ITEM:
            return self._create_general_item(clipboard_data)
        else:
            return None

    def _create_currency_item(self, data):
        data_sections = get_all_sections(data)
        trade_name = data_sections[0].split(LINE_FEED)[1].strip()
        
        self.logger.debug("Creating currency item : {}".format(trade_name))

        stack_size = data_sections[1].split("Stack Size: ")[1].split("/")[0].strip()
        stack_max_size = data_sections[1].split("/")[1].strip()
        item = CurrencyItem(Currency(trade_name, stack_max_size), stack_size)
        self.logger.debug("Created currency [{}]".format(str(item)))

        return item

    def _create_general_item(self, data):
        self.logger.debug("Creating general item")
        data_sections = get_all_sections(data)
        name_section = data_sections[0].split(LINE_FEED)[0]

        rarity = name_section[0].split("Rarity: ")[1].strip()
        name = " ".join([name_section[1], name_section[2]]).strip()
        self.logger.debug("Creating non-currency item : {}.{}".format(rarity, name))

        item = Item(name, rarity)
        self.logger.debug("Created item [{}]".format(str(item)))

        return item
