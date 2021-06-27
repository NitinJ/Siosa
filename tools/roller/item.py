import logging
import re

from tools.roller.clipboard import Clipboard


class Affix:
    PREFIX = "prefix modifier"
    SUFFIX = "suffix modifier"
    UNIQUE = "unique modifier"
    AFFIX_DETAILS_REGEX = re.compile('{ (.*) modifier "(.*)" \(tier: (\d*)\)')
    AFFIX_VALUE_RANGE_REGEX = re.compile("\((.*?)\)")

    def __init__(self, str_val, name, tier, type):
        self.str_val = str_val
        self.name = name
        self.tier = tier
        self.type = type

    def _str(self):
        return "{}-{}-T{}".format(self.type, self.name, self.tier)

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
        return Affix(",".join(affix_str_lines), groups[1], int(groups[2]),
                     groups[0])


class Item:
    SECTION_SEPARATOR = "--------\r\n"
    LINE_FEED = "\r\n"
    NEWLINE = "\n"
    RARITY_STR = "rarity: "
    ITEM_CLASS_STR = "item class: "
    logger = logging.getLogger(__name__)
    logger.setLevel('DEBUG')

    @staticmethod
    def create_from_clipboard_data(clipboard_data):
        item_class = Item.get_item_class(clipboard_data)
        rarity = Item.get_rarity(clipboard_data)
        name = Item.get_name(rarity, clipboard_data)
        affixes = []
        if rarity != 'unique':
            # No support for unique mods as of now. Not required.
            affixes = Item.parse_affixes(
                Item.get_all_mods(rarity, clipboard_data))
        return Item(item_class, rarity, name, affixes)

    def __init__(self, item_class, rarity, name, affixes):
        self.item_class = item_class
        self.rarity = rarity
        self.name = name
        self.affixes = affixes

    def __repr__(self):
        return self._str()

    def _str(self):
        return "Name: {},\nRarity: {},\nClass: {},\nAffixes({}): {}".format(
            self.name,
            self.rarity,
            self.item_class,
            len(self.affixes),
            ", ".join([str(affix) for affix in self.affixes]))

    def __str__(self):
        return self._str()

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

    @staticmethod
    def parse_affixes(mods):
        return [Affix.create_from_clipboard_affix(mod) for mod in mods]

    @staticmethod
    def get_item_class(clipboard_data):
        first_line = clipboard_data.split(Item.LINE_FEED)[0]
        r = first_line.find(Item.ITEM_CLASS_STR)
        item_class = first_line[r + len(Item.ITEM_CLASS_STR):].strip().lower()
        return item_class

    @staticmethod
    def get_rarity(clipboard_data):
        name_section_lines = clipboard_data.split(Item.SECTION_SEPARATOR)[
            0].split(
            Item.LINE_FEED)
        rarity = None
        for line in name_section_lines:
            r = line.find(Item.RARITY_STR)
            if r == -1:
                continue
            rarity = line[r + len(Item.RARITY_STR):].strip().lower()
            break
        return rarity

    @staticmethod
    def get_name(rarity, clipboard_data):
        name_section = clipboard_data.split("--------\r\n")[0]
        return " ".join(name_section.split(Item.LINE_FEED)[2:]).lower().strip()

    @staticmethod
    def get_all_mods(rarity, clipboard_data):
        mods_section = Item.get_mod_section(rarity, clipboard_data)
        mods = []
        # Each affix in the mod section has 1 line for the affix details like
        # tier, name etc. and following multiple lines for the actual affix
        # Hybrid affixes take multiple lines. Each affix is separated by a
        # line feed and within each affix, each line is separated by a newline.
        for affix in mods_section.strip().split(Item.LINE_FEED):
            affix_lines = affix.split("\n")
            mods.extend([affix_lines])
        Item.logger.debug("All item mods: {}".format(mods))
        return mods

    @staticmethod
    def get_mod_section(rarity, clipboard_data):
        if rarity == 'normal':
            return ''
        sections = clipboard_data.split(Item.SECTION_SEPARATOR)
        for section in sections:
            if any([x in section
                    for x in [Affix.PREFIX, Affix.SUFFIX, Affix.UNIQUE]]):
                return section


if __name__ == "__main__":
    item = Item.create_from_clipboard_data(Clipboard().get_clipboard_data())
    print(item)