from siosa.common.decorations import override
from siosa.data.poe_item import Item, ItemType


class Gem(Item):
    def __init__(self, level, quality, item_info):
        """
        Args:
            name:
        """
        super().__init__(item_info=item_info, item_type=ItemType.GEM)
        self.level = level
        self.quality = quality

    @override
    def get_trade_name(self):
        return "Level {} {}% {}".format(self.level, self.quality,
                                        self.item_info['type_line'])

    def __str__(self):
        return "{}, level: {}, quality: {}".format(
            super().__str__(), self.level, self.quality)

    def __eq__(self, other):
        return super().__eq__(other) and \
               self.level == other.level and \
               self.quality == other.quality
