from enum import Enum
from data.poe_item import ItemType

LINE_FEED = '\r\n'
SECTION_SEPARATOR = '--------' + LINE_FEED

def get_clipboard_item_type(data):
        data_sections = data.split(SECTION_SEPARATOR)
        if not data or not data_sections or not data_sections[0]:
            return ItemType.UNKNOWN
        type_name_section = data_sections[0].split(LINE_FEED)[0]
        if type_name_section.split("Rarity: ")[1].strip() == "Currency":
            return ItemType.CURRENCY
        else:
            return ItemType.ITEM

def get_all_sections(data):
     return data.split(SECTION_SEPARATOR)