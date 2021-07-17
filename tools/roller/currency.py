from enum import Enum


class Currency(Enum):
    ALTERATION = 'Orb of Alteration'
    AUGMENTATION = 'Orb of Augmentation'
    REGAL = 'Regal Orb'
    SCOURING = 'Orb of Scouring'
    TRANSMUTATION = 'Orb of Transmutation'
    CHANCE = 'Orb of Chance'
    ALCHEMY = 'Orb of Alchemy'
    CHAOS = 'Chaos Orb'


class CurrencyStack:
    LINE_FEED = "\r\n"
    SEPARATOR = "--------\r\n"

    def __init__(self, type, stack, stack_size):
        """
        Args:
            type:
            stack:
            stack_size:
        """
        self.type = type
        self.stack = stack
        self.stack_size = stack_size

    @staticmethod
    def create_from_clipboard_data(data):
        """
        Args:
            data:
        """
        name_section = data.split(CurrencyStack.SEPARATOR)[0]
        stack_section = data.split(CurrencyStack.SEPARATOR)[1]
        rarity = \
            name_section.split(CurrencyStack.LINE_FEED)[1].split("rarity: ")[1]
        if not rarity == "currency":
            return None
        currency_type = name_section.split(CurrencyStack.LINE_FEED)[2].strip()
        stack_data = stack_section.split("stack size: ")[1]
        stack = int(stack_data.split("/")[0].replace(",", ""))
        stack_size = int(stack_data.split("/")[1].strip())
        return CurrencyStack(currency_type, stack, stack_size)
