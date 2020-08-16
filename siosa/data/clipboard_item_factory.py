import logging

from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.poe_currencies import *
from siosa.data.poe_item import ItemType
from siosa.network.poe_api import PoeApi
from siosa.resources.resource import Resource

LINE_FEED = '\r\n'
SECTION_SEPARATOR = '--------' + LINE_FEED
INFLUENCES = Resource.get('influences')

class ClipboardItemFactory:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.poe_api = PoeApi()
        self.exchange = CurrencyExchange()
        
    def get_item(self, clipboard_data):
        if not clipboard_data or clipboard_data.find(LINE_FEED) == -1:
            return None
        self.logger.debug("Getting item from clipboard data")

        data_sections = self._get_all_sections(clipboard_data)
        type = self._get_clipboard_item_type(data_sections)
        self.logger.debug("Got {} from clipboard".format(type))

        if type == ItemType.CURRENCY:
            return self._create_currency_item_from_clipboard(data_sections)
        elif type == ItemType.ITEM:
            return self._create_general_item_from_clipboard(data_sections)
        return None

    def _create_currency_item_from_clipboard(self, data_sections):
        # name for currency is it's type_line.
        name = self._get_type_line(data_sections)
        stack_size = self._get_stack_size(data_sections)
        stack_max_size = self._get_max_stack_size(data_sections)

        info = {
            'note': self._get_note(data_sections)
        }
        currency = self.exchange.create_currency(
            name=name,
            stack_max_size=stack_max_size)
        if not currency:
            return None

        item = CurrencyStack(currency, stack_size, item_info=info)
        self.logger.debug("Created currency item [{}]".format(str(item)))
        return item

    def _get(self, obj, key, fallback):
        return obj[key] if key in obj.keys() else fallback
    
    def _create_general_item_from_clipboard(self, data_sections):
        self.logger.debug("Creating general item")
        info = {
            'rarity': self._get_rarity(data_sections),
            'name': self._get_name(data_sections),
            'type_line': self._get_type_line(data_sections),
            'ilvl': self._get_item_level(data_sections),
            'corrupted': self._get_corrupted(data_sections),
            'unidentified': self._get_unidentified(data_sections),
            'note': self._get_note(data_sections),
            'influences': self._get_influences(data_sections)
        }
        item = Item(item_info=info, item_type=ItemType.ITEM)
        self.logger.debug("Created general item [{}]".format(str(item)))
        return item

    def _get_clipboard_item_type(self, data_sections):
        if not len(data_sections) or not data_sections[0]:
            return ItemType.UNKNOWN
        rarity = self._get_rarity(data_sections)
        if rarity == "Currency":
            return self._get_currency_item_type(data_sections)
        elif rarity == "Divination Card":
            return ItemType.DIVINATION_CARD
        elif rarity == "Gem":
            return ItemType.GEM
        else:
            return self._get_item_type(data_sections)

    def _get_item_type(self, data_sections):
        rarity = self._get_rarity(data_sections)
        if self._is_scarab(data_sections, rarity):
            return ItemType.SCARAB
        elif self._is_fragment(data_sections, rarity):
            return ItemType.FRAGMENT
        elif self._is_map(data_sections, rarity):
            return ItemType.MAP
        # TODO: Add support for more ItemTypes.
        return ItemType.ITEM
        
    def _get_currency_item_type(self, data_sections):
        if self._is_delirium_orb(data_sections):
            return ItemType.DELIRIUM_ORB
        elif self._is_catalyst(data_sections):
            return ItemType.CATALYST
        elif self._is_oil(data_sections):
            return ItemType.OIL
        elif self._is_delve_fossil(data_sections):
            return ItemType.DELVE_FOSSIL
        elif self._is_delve_resonator(data_sections):
            return ItemType.DELVE_RESONATOR
        return ItemType.CURRENCY

    def _is_map(self, data_sections, rarity):
        try:
            return data_sections[1][0].startswith("Map Tier:") and \
                data_sections[5][0] == "Travel to this Map by using it in a personal Map Device. Maps can only be used once." and \
                len(data_sections[5]) == 1
        except:
            return False
        
    def _is_fragment(self, data_sections, rarity):
        try:
            return rarity == 'Normal' and \
                data_sections[0][1].endswith("Scarab") and \
                data_sections[2][0] == "Can be used in a personal Map Device." and \
                len(data_sections[2]) == 1
        except:
            return False
        
    def _is_scarab(self, data_sections, rarity):
        try:
            return rarity == 'Normal' and \
                data_sections[0][1].endswith("Scarab") and \
                data_sections[3][0].find("Can be used in a personal Map Device to add modifiers to a Map.") > -1
        except:
            return False

    def _is_delve_resonator(self, data_sections):
        try:
            return data_sections[0][1].find("Resonator") > -1 and \
                data_sections[4][0].find("All sockets must be filled with Fossils before this item can be used.") > -1
        except:
            return False
        
    def _is_delve_fossil(self, data_sections):
        try:
            return data_sections[0][1].find("Fossil") > -1 and \
                data_sections[3][0].find("Place in a Resonator to influence item crafting.") > -1
        except:
            return False
        
    def _is_oil(self, data_sections):
        try:
            return data_sections[0][1].find("Oil") > -1 and \
                data_sections[2][0].find("Can be combined with other Oils at Cassia to Enchant") > -1
        except:
            return False
    
    def _is_catalyst(self, data_sections):
        try:
            return data_sections[0][1].find("Catalyst") > -1 and \
                data_sections[2][0].find("Adds quality that enhances") > -1
        except:
            return False

    def _is_delirium_orb(self, data_sections):
        return data_sections[0][1].find("Delirium Orb") > -1
        
    def _get_all_sections(self, data):
        data = data.split(SECTION_SEPARATOR)
        sections = []
        for section in data:
            section_lines = [line.strip() for line in section.split(LINE_FEED)]
            sections.append(section_lines[:-1])
        self.logger.debug(sections)
        return sections

    def _get_rarity(self, sections):
        return sections[0][0].split("Rarity: ")[1].strip()
       
    def _get(self, obj, key, fallback):
        return obj[key] if key in obj.keys() else fallback
 
    
    def _get_name(self, sections):
        return sections[0][1] if len(sections[0]) == 3 else ''

    def _get_type_line(self, sections):
        try:
            return (sections[0][2] if len(sections[0]) == 3 else sections[0][1])
        except Exception as e:
            self.logger.error(e)
            return ''

    def _get_item_level(self, sections):
        level = ''
        for section in sections:
            for line in section:
                if line.find("Item Level: ") > -1 and len(section) == 1:
                    level = int(line.split("Item Level: ")[1].strip())
                    break
        return level

    def _get_stack_size(self, sections):
        try:
            for section in sections:
                for line in section:
                    if line.find("Stack Size: ") > -1 and len(section) == 1:
                        return int(line.split("Stack Size: ")[1].split("/")[0].replace(",", ""))
        except Exception as e:
            self.logger.error(e)
            return ''

    def _get_max_stack_size(self, sections):
        try:
            for section in sections:
                for line in section:
                    if line.find("Stack Size: ") > -1 and len(section) == 1:
                        return int(line.split("Stack Size: ")[1].split("/")[1].replace(",", ""))
        except Exception as e:
            self.logger.error(e)
            return ''

    def _get_corrupted(self, sections):
        for section in sections:
            for line in section:
                if line == "Corrupted":
                    return len(section) == 1
        return ''

    def _get_unidentified(self, sections):
        for section in sections:
            for line in section:
                if line == "Unidentified":
                    return len(section) == 1
        return ''

    def _get_note(self, sections):
        for section in sections:
            for line in section:
                if line.find("Note: ") > -1 and len(section) == 1:
                    return line.split("Note: ")[1].strip()
        return ''

    def _get_influences(self, sections):
        influences = {}
        for section in sections:
            influence_section = False
            for line in section:
                influence_section = sum(
                    [line.find(influence) > -1 for influence in INFLUENCES]) != 0
            if not influence_section:
                continue
            for line in section:
                for influence in INFLUENCES:
                    if line.find(influence) == 0:
                        influences[influence] = True
            return influences
        return influences
