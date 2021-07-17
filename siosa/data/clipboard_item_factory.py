from scanf import scanf

from siosa.data.affix import Affix
from siosa.data.poe_currencies import *
from siosa.data.poe_item import ItemType
from siosa.network.poe_api import PoeApi

LINE_FEED = '\r\n'
NEW_LINE = '\n'
SECTION_SEPARATOR = '--------' + LINE_FEED
INFLUENCES = [
    'Shaper',
    'Elder',
    'Crusader',
    'Warlord',
    'Hunter',
    'Redeemer',
]


class ClipboardItemFactory:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.poe_api = PoeApi()

    def get_item(self, clipboard_data):
        """
        Args:
            clipboard_data:
        """
        if not clipboard_data or clipboard_data.find(LINE_FEED) == -1:
            return None
        self.logger.debug("Getting item from clipboard data")

        data_sections = self._get_all_sections(clipboard_data)
        type = self._get_clipboard_item_type(data_sections)
        rarity = self._get_rarity(data_sections)
        self.logger.debug(
            "Got rarity({}), type({}) from clipboard".format(rarity, type))

        # TODO: Handle other rarities like divination card, gem etc.
        if rarity == 'currency':
            return self._create_currency_item(type, data_sections)
        else:
            return self._create_general_item(type, rarity, data_sections)

    def _create_currency_item(self, type, data_sections):
        """
        Args:
            type:
            data_sections:
        """
        type_line = self._get_type_line('currency', True, data_sections)
        stack_size = self._get_stack_size(data_sections)
        stack_max_size = self._get_max_stack_size(data_sections)

        info = {
            'type_line': type_line,
            'base_type': type_line,
            'note': self._get_note(data_sections)
        }
        currency = Currency.create(
            name=type_line, max_stack_in_trade=stack_max_size)
        if not currency:
            self.logger.warning(
                "Couldn't create currency item({}, {})".format(type_line, type))
            return None

        item = CurrencyStack(currency, stack_size,
                             item_type=type, item_info=info)
        self.logger.debug("Created currency item [{}]".format(str(item)))
        return item

    def _get(self, obj, key, fallback):
        """
        Args:
            obj:
            key:
            fallback:
        """
        return obj[key] if key in obj.keys() else fallback

    def _parse_affixes(self, mods):
        """
        Args:
            mods:
        """
        return [Affix.create_from_clipboard_affix(mod) for mod in mods]

    def _get_num_prefixes(self, affixes):
        """
        Args:
            affixes:
        """
        return len([x for x in affixes if x.is_prefix()])

    def _get_num_suffixes(self, affixes):
        """
        Args:
            affixes:
        """
        return len([x for x in affixes if x.is_suffix()])

    def _get_is_synthesized(self, data_sections):
        """
        Args:
            data_sections:
        """
        for section in data_sections:
            for section_line in section:
                if "Synthesised Item" in section_line:
                    return True
        return False

    def _create_general_item(self, type, rarity, data_sections):
        """
        Args:
            type:
            rarity:
            data_sections:
        """
        self.logger.debug("Creating general item")

        try:
            # TODO: Use these affix objects to create more metadata for item.
            affixes = self._parse_affixes(
                self._get_all_mods(rarity, data_sections))
        except:
            affixes = []

        identified = not self._get_unidentified(data_sections)
        info = {
            'rarity': rarity,
            'name': self._get_name(rarity, identified, data_sections),
            'type_line': self._get_type_line(rarity, identified, data_sections),
            'base_type': self._get_base_type(rarity, affixes, identified, data_sections),
            'ilvl': self._get_item_level(data_sections),
            'corrupted': self._get_corrupted(data_sections),
            'identified': not self._get_unidentified(data_sections),
            'note': self._get_note(data_sections),
            'explicit_mods': [affix.str_val for affix in affixes],
            'n_prefixes': self._get_num_prefixes(affixes),
            'n_suffixes': self._get_num_suffixes(affixes),
            'influences': self._get_influences(data_sections),
            'synthesized': self._get_is_synthesized(data_sections)
        }
        item = Item(item_info=info, item_type=type)
        self.logger.debug("Created general item [{}]".format(str(item)))
        return item

    def _get_clipboard_item_type(self, data_sections):
        """
        Args:
            data_sections:
        """
        if not len(data_sections) or not data_sections[0]:
            return ItemType.UNKNOWN
        rarity = self._get_rarity(data_sections)
        if rarity == "currency":
            return self._get_currency_item_type(data_sections)
        elif rarity == "divination Card":
            return ItemType.DIVINATION_CARD
        elif rarity == "gem":
            return ItemType.GEM
        else:
            return self._get_item_type(data_sections)

    def _get_currency_item_type(self, data_sections):
        """
        Args:
            data_sections:
        """
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
        # elif self._is_essence(data_sections):
        #     return ItemType.ESSENCE
        elif self._is_splinter(data_sections):
            return ItemType.SPLINTER
        elif self._is_simulacrum_splinter(data_sections):
            return ItemType.SIMULACRUM_SPLINTER
        # TODO: Add support for more currency types.
        return ItemType.CURRENCY

    def _get_item_type(self, data_sections):
        """
        Args:
            data_sections:
        """
        rarity = self._get_rarity(data_sections)
        if self._is_scarab(data_sections, rarity):
            return ItemType.SCARAB
        elif self._is_fragment(data_sections, rarity):
            return ItemType.FRAGMENT
        elif self._is_map(data_sections, rarity):
            return ItemType.MAP
        elif self._is_offering(data_sections):
            return ItemType.OFFERING
        elif self._is_divine_vessel(data_sections):
            return ItemType.DIVINE_VESSEL
        elif self._is_timeless_emblem(data_sections):
            return ItemType.TIMELESS_EMBLEM
        elif self._is_breachstone(data_sections):
            return ItemType.BREACHSTONE
        # TODO: Add support for more ItemTypes.
        return ItemType.ITEM

    def _get_mod_section(self, rarity, data_sections):
        """
        Args:
            rarity:
            data_sections:
        """
        if rarity == 'normal':
            return []
        for section in data_sections:
            for section_line in section:
                if any([x in section_line
                        for x in [Affix.PREFIX, Affix.SUFFIX, Affix.UNIQUE]]):
                    return section
        return []

    def _get_all_mods(self, rarity, data_sections):
        """
        Args:
            rarity:
            data_sections:
        """
        mods_section = self._get_mod_section(rarity, data_sections)
        mods = []
        # Each affix in the mod section has 1 line for the affix details like
        # tier, name etc. and following multiple lines for the actual affix
        # Hybrid affixes take multiple lines. Each affix is separated by a
        # line feed and within each affix, each line is separated by a newline.
        for affix in mods_section:
            affix_lines = affix.split(NEW_LINE)
            mods.extend([affix_lines])
        return mods

    def _is_divine_vessel(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return data_sections[0][1] == "Divine Vessel"
        except:
            return False

    def _is_offering(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return data_sections[0][1] == "Offering to the Goddess"
        except:
            return False

    def _is_timeless_emblem(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return scanf("Timeless %s Emblem", data_sections[0][1]) and \
                   data_sections[1][
                       0] == "Place two or more different Emblems in " \
                             "a Map Device to access the Domain of Timeless Conflict. " \
                             "Can only be used once."
        except:
            return False

    def _is_breachstone(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return data_sections[0][1].find("Breachstone") > -1 and \
                   scanf(
                       "Travel to %s Domain by using this item in a personal Map Device",
                       data_sections[1][0])
        except:
            return False

    def _is_simulacrum_splinter(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return data_sections[0][1] == "Simulacrum Splinter" and \
                   scanf("Combine %d Splinters to create a Simulacrum.",
                         data_sections[2][0])
        except:
            return False

    def _is_splinter(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            # Some splinter section lines have 'Splinters' and some have 
            # 'splinters' :/
            info_section = data_sections[2][0].lower()
            return data_sections[0][1].find("Splinter") > -1 and \
                   scanf("combine %d splinters to create", info_section)
        except:
            return False

    def _is_map(self, data_sections, rarity):
        """
        Args:
            data_sections:
            rarity:
        """
        try:
            return data_sections[1][0].startswith("Map Tier:") and \
                   data_sections[5][
                       0] == "Travel to this Map by using it in a personal Map Device. Maps can only be used once." and \
                   len(data_sections[5]) == 1
        except:
            return False

    def _is_fragment(self, data_sections, rarity):
        """
        Args:
            data_sections:
            rarity:
        """
        try:
            return rarity == 'normal' and \
                   data_sections[2][
                       0] == "Can be used in a personal Map Device." and \
                   len(data_sections[2]) == 1
        except:
            return False

    def _is_scarab(self, data_sections, rarity):
        """
        Args:
            data_sections:
            rarity:
        """
        try:
            return rarity == 'normal' and \
                   data_sections[0][1].endswith("Scarab") and \
                   data_sections[3][0].find(
                       "Can be used in a personal Map Device to add modifiers to a Map.") > -1
        except:
            return False

    def _is_delve_resonator(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return data_sections[0][1].find("Resonator") > -1 and \
                   data_sections[4][0].find(
                       "All sockets must be filled with Fossils before this item can be used.") > -1
        except:
            return False

    def _is_essence(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return (
                           data_sections[0][1].find(" Essence of ") > -1
                           and data_sections[3][0].find(
                       "Right click this item then left click a ")
                           > -1
                   ) or (
                           data_sections[0][1] == "Remnant of Corruption"
                           and data_sections[2][0]
                           == "Corrupts the Essences trapping a monster, modifying them unpredictably"
                   )
        except:
            return False

    def _is_delve_fossil(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return data_sections[0][1].find("Fossil") > -1 and \
                   data_sections[3][0].find(
                       "Place in a Resonator to influence item crafting.") > -1
        except:
            return False

    def _is_oil(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return data_sections[0][1].find("Oil") > -1 and \
                   data_sections[2][0].find(
                       "Can be combined with other Oils at Cassia to Enchant") > -1
        except:
            return False

    def _is_catalyst(self, data_sections):
        """
        Args:
            data_sections:
        """
        try:
            return data_sections[0][1].find("Catalyst") > -1 and \
                   data_sections[2][0].find("Adds quality that enhances") > -1
        except:
            return False

    def _is_delirium_orb(self, data_sections):
        """
        Args:
            data_sections:
        """
        return data_sections[0][1].find("Delirium Orb") > -1

    def _get_all_sections(self, data):
        """
        Args:
            data:
        """
        data = data.split(SECTION_SEPARATOR)
        sections = []
        for section in data:
            section_lines = [line.strip() for line in section.split(LINE_FEED)]
            sections.append(section_lines[:-1])
        self.logger.debug(sections)
        return sections

    def _get_rarity(self, sections):
        """
        Args:
            sections:
        """
        return sections[0][1].split("Rarity: ")[1].strip().lower()

    def _get_name(self, rarity, identified, sections):
        """
        Args:
            rarity:
            identified:
            sections:
        """
        if rarity in ('normal', 'magic'):
            return ""
        elif rarity in ('rare', 'unique') and identified:
            return sections[0][2]
        return ""

    def _get_type_line(self, rarity, identified, sections):
        """
        Args:
            rarity:
            identified:
            sections:
        """
        try:
            if rarity in ('rare', 'unique') and identified:
                return sections[0][3]
            return sections[0][2]
        except Exception as e:
            self.logger.error(e)
            return ''

    def _get_base_type(self, rarity, affixes, identified, sections):
        """
        Args:
            rarity:
            affixes:
            identified:
            sections:
        """
        base_type = None
        try:
            if rarity == 'normal':
                base_type = sections[0][2]
            elif rarity == 'magic':
                base_type = sections[0][2]
                base_type = base_type.split(" of ")[0]
                if self._get_num_prefixes(affixes) > 0:
                    base_type = " ".join(base_type.split(" ")[1:])
            elif rarity in ('rare', 'unique') and identified:
                base_type = sections[0][3]
            else :
                base_type = sections[0][2]

            if self._get_is_synthesized(sections):
                base_type = base_type.replace("Synthesised ", "")

            return base_type
        except Exception as e:
            self.logger.error(e)
            return ''

    def _get_item_level(self, sections):
        """
        Args:
            sections:
        """
        level = ''
        for section in sections:
            for line in section:
                if line.find("Item Level: ") > -1 and len(section) == 1:
                    level = int(line.split("Item Level: ")[1].strip())
                    break
        return level

    def _get_stack_size(self, sections):
        """
        Args:
            sections:
        """
        try:
            for section in sections:
                for line in section:
                    if line.find("Stack Size: ") > -1 and len(section) == 1:
                        return int(
                            line.split("Stack Size: ")[1].split("/")[0].replace(
                                ",", ""))
        except Exception as e:
            self.logger.error(e)
            return ''

    def _get_max_stack_size(self, sections):
        """
        Args:
            sections:
        """
        try:
            for section in sections:
                for line in section:
                    if line.find("Stack Size: ") > -1 and len(section) == 1:
                        return int(
                            line.split("Stack Size: ")[1].split("/")[1].replace(
                                ",", ""))
        except Exception as e:
            self.logger.error(e)
            return ''

    def _get_corrupted(self, sections):
        """
        Args:
            sections:
        """
        for section in sections:
            for line in section:
                if line == "Corrupted":
                    return len(section) == 1
        return ''

    def _get_unidentified(self, sections):
        """
        Args:
            sections:
        """
        for section in sections:
            for line in section:
                if line == "Unidentified" and len(section) == 1:
                    return True
        return False

    def _get_note(self, sections):
        """
        Args:
            sections:
        """
        for section in sections:
            for line in section:
                if line.find("Note: ") > -1 and len(section) == 1:
                    return line.split("Note: ")[1].strip()
        return ''

    def _get_influences(self, sections):
        """
        Args:
            sections:
        """
        influences = {}
        for section in sections:
            influence_section = False
            for line in section:
                influence_section = sum(
                    [line.find(influence) > -1 for influence in
                     INFLUENCES]) != 0
            if not influence_section:
                continue
            for line in section:
                for influence in INFLUENCES:
                    if line.find(influence) == 0:
                        influences[influence] = True
            return influences
        return influences
