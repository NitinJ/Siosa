from siosa.common.decorations import override
from siosa.data.poe_item import Item, ItemType


class Map(Item):
    def __init__(self, tier, item_info):
        """
        Args:
            name:
        """
        super().__init__(item_info=item_info, item_type=ItemType.MAP)
        self.tier = tier

    @override
    def get_trade_name(self):
        return "{} (T{})".format(super().get_trade_name(), self.tier)

    def __str__(self):
        return "{}, tier: {} ".format(super().__str__(), self.tier)

    def __eq__(self, other):
        return super().__eq__(other) and self.tier == other.tier
