from tools.roller.currency import Currency


class Locations:
    CURRENCY_LOCATIONS = {
        Currency.ALTERATION: (114, 263, 114, 263),
        Currency.AUGMENTATION: (233, 318, 233, 318),
        Currency.REGAL: (431, 263, 431, 263),
        Currency.SCOURING: (176, 445, 176, 445),
        Currency.TRANSMUTATION: (56, 268, 56, 268),
        Currency.CHANCE: (230, 264, 230, 264),
        Currency.CHAOS: (546, 264, 546, 264),
        Currency.ALCHEMY: (490, 264, 490, 264)
    }
    ITEM_LOCATION = (336, 419, 336, 419)
    INVENTORY_00 = (1295, 615, 1295, 615)

    @staticmethod
    def get_inventory00():
        return Locations.INVENTORY_00

    @staticmethod
    def get_currency_location(currency):
        if currency not in Locations.CURRENCY_LOCATIONS.keys():
            return None
        return Locations.CURRENCY_LOCATIONS[currency]

    @staticmethod
    def get_item_location():
        return Locations.ITEM_LOCATION