import logging
import re
from pprint import pformat

class Affix:
    PREFIX = "prefix modifier"
    SUFFIX = "suffix modifier"
    AFFIX_DETAILS_REGEX = re.compile('{ (.*) modifier "(.*)" \(tier: (\d*)\)')
    AFFIX_VALUE_RANGE_REGEX = re.compile("\((.*)\)")

    def __init__(self, str_val, name, tier, type):
        self.str_val = str_val
        self.name = name
        self.tier = tier
        self.type = type

    def _str(self):
        return "{}({}):T-{}".format(self.type, self.name, self.tier)

    def __str__(self):
        return self._str()

    def __repr__(self):
        return self._str()

    def is_prefix(self):
        return self.type == 'prefix'

    @staticmethod
    def create_from_clipboard_affix(affix_arr):
        affix_details = affix_arr[0]
        match = Affix.AFFIX_DETAILS_REGEX.match(affix_details)
        if not match:
            return None
        groups = match.groups()
        affix_str_lines = []
        for affix_line in affix_arr[1:]:
            affix_line = affix_line.replace(" — unscalable value", "")
            affix_line = re.sub(Affix.AFFIX_VALUE_RANGE_REGEX, '', affix_line)
            affix_str_lines.append(affix_line)
        return Affix(",".join(affix_str_lines), groups[1], int(groups[2]), groups[0])


class Item:
    SECTION_SEPARATOR = "--------\r\n"
    LINE_FEED = "\r\n"
    NEWLINE = "\n"
    RARITY_STR = "rarity: "
    ITEM_CLASS_STR = "item class: "

    def __init__(self, clipboard_data):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.clipboard_data = clipboard_data
        self.item_class = 'unknown'
        self.rarity = 'unknown'
        self.name = 'unknown'
        self.mods = []
        self.affixes = []
        self._parse_clipboard_data()
        self._parse_affixes()

    def __str__(self):
        return "Name: {}, Rarity: {}, class: {}, affixes({})".format(
            self.name,
            self.rarity,
            self.item_class,
            "\n".join([str(affix) for affix in self.affixes]))

    def get_prefixes(self):
        return [x for x in self.affixes if x.is_prefix()]

    def get_suffixes(self):
        return [x for x in self.affixes if not x.is_prefix()]

    def get_num_affixes(self):
        return len(self.affixes)

    def get_num_prefixes(self):
        return len([x for x in self.affixes if x.is_prefix()])

    def get_num_suffixes(self):
        return self.get_num_affixes() - self.get_num_prefixes()

    def _parse_affixes(self):
        for mod in self.mods:
            self.affixes.append(Affix.create_from_clipboard_affix(mod))

    def _parse_clipboard_data(self):
        self.item_class = Item.get_item_class(self.clipboard_data)
        self.rarity = Item.get_rarity(self.clipboard_data)
        self.name = self.get_name(self.clipboard_data)
        self.mods = self.get_all_mods(self.clipboard_data)

    @staticmethod
    def get_item_class(data):
        first_line = data.split(Item.LINE_FEED)[0]
        r = first_line.find(Item.ITEM_CLASS_STR)
        item_class = first_line[r + len(Item.ITEM_CLASS_STR):].strip().lower()
        return item_class

    @staticmethod
    def get_rarity(data):
        name_section_lines = data.split(Item.SECTION_SEPARATOR)[0].split(
            Item.LINE_FEED)
        rarity = None
        for line in name_section_lines:
            r = line.find(Item.RARITY_STR)
            if r == -1:
                continue
            rarity = line[r + len(Item.RARITY_STR):].strip().lower()
            break
        return rarity

    def get_name(self, data):
        name = ''
        name_section = data.split("--------\r\n")[0]
        if self.rarity == 'magic':
            name = name_section.split(Item.LINE_FEED)[2].strip().lower()
        elif self.rarity == 'rare':
            name = " ".join(name_section.split(Item.LINE_FEED)[2:]).lower()
        return name

    def get_all_mods(self, data):
        mods_section = self.get_mod_section(data)
        mods = []
        # Each affix in the mod section has 1 line for the affix details like
        # tier, name etc. and following multiple lines for the actual affix
        # Hybrid affixes take multiple lines. Each affix is separated by a
        # line feed and within each affix, each line is separated by a newline.
        for affix in mods_section.strip().split(Item.LINE_FEED):
            affix_lines = affix.split("\n")
            mods.extend([affix_lines])
        self.logger.debug("All item mods: {}".format(mods))
        return mods

    def get_mod_section(self, data):
        if self.rarity == 'normal':
            return ''
        sections = data.split(Item.SECTION_SEPARATOR)
        for section in sections:
            if section.find(Affix.PREFIX) > -1 or \
                    section.find(Affix.SUFFIX) > -1:
                return section
