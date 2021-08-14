import re


class Affix:
    # TODO: Move everything to lower case.
    PREFIX = "Prefix Modifier"
    SUFFIX = "Suffix Modifier"
    UNIQUE = "Unique Modifier"
    AFFIX_DETAILS_REGEX = re.compile('{ (.*) Modifier "(.*)" \(Tier: (\d*)\)')
    UNIQUE_AFFIX_DETAILS_REGEX = re.compile('{ Unique Modifier ')
    CRAFTED_AFFIX_DETAILS_REGEX = re.compile(
        '{ Master Crafted (.*) Modifier "(.*)" \(Rank: (\d*)\)')
    AFFIX_VALUE_RANGE_REGEX = re.compile("\((.*?)\)")

    def __init__(self, str_val, name, tier, type, crafted=False,
                 fractured=False):
        """
        Args:
            str_val:
            name:
            tier:
            type:
            crafted:
            fractured:
        """
        self.str_val = str_val
        self.name = name
        self.tier = tier
        self.type = type
        self.crafted = crafted
        self.fractured = fractured

    def _str(self):
        return "{}-{}-T{}".format(self.type, self.name, self.tier)

    def __str__(self):
        return self._str()

    def __repr__(self):
        return self._str()

    def is_prefix(self):
        return self.type == 'Prefix'

    def is_unique(self):
        return self.type == 'Unique'

    def is_suffix(self):
        return self.type == 'Suffix'

    @staticmethod
    def _get_details(affix_details):
        """
        Args:
            affix_details:
        """
        crafted = False
        match = Affix.UNIQUE_AFFIX_DETAILS_REGEX.match(affix_details)
        if match:
            return '', 0, 'unique'

        match = Affix.AFFIX_DETAILS_REGEX.match(affix_details)
        if match:
            groups = match.groups()
            return groups[1], int(groups[2]), groups[0]

        match = Affix.CRAFTED_AFFIX_DETAILS_REGEX.match(affix_details)
        if match:
            groups = match.groups()
            return groups[1], int(groups[2]), groups[0]

    @staticmethod
    def create_from_clipboard_affix(affix_arr):
        """
        Args:
            affix_arr:
        """
        affix_details = affix_arr[0]
        fractured = False

        name, tier, type = Affix._get_details(affix_details)
        crafted = (name == 'Upgraded')
        affix_str_lines = []
        for affix_line in affix_arr[1:]:
            affix_line = affix_line.replace(" Unscalable Value", "")
            affix_line = re.sub(Affix.AFFIX_VALUE_RANGE_REGEX, '', affix_line)

            if affix_line.find("fractured"):
                fractured = True
                affix_line = affix_line.replace(" (fractured)", "")

            affix_str_lines.append(affix_line)

        return Affix(",".join(affix_str_lines), name, tier, type,
                     crafted=crafted, fractured=fractured)
