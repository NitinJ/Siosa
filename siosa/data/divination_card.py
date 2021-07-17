from siosa.data.poe_item import Item


class DivinationCard():
    def __init__(self, name, max_stack_size, gives):
        """
        Args:
            name:
            max_stack_size:
            gives:
        """
        self.name = name
        self.max_stack_size = max_stack_size
        self.gives = gives

    def __str__(self):
        return "name: {}, max_stack: {}, gives: {}".format(
            self.name, self.max_stack_size, self.gives)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            val = other.name == self.name
            val = val and other.max_stack_size == self.max_stack_size
            val = val and other.gives == self.gives
            return val
        return False


class DivinationCardStack(Item):
    def __init__(self, card, quantity, item_info={}):
        """
        Args:
            card:
            quantity:
            item_info:
        """
        self.card = card
        self.quantity = quantity
        info = {
            'rarity': 'Currency',
            'type_line': card,
            'stack_size': quantity,
            'max_stack_size': currency.max_stack_in_trade
        }
        item_info.update(info)
        Item.__init__(self, item_info=item_info, item_type=ItemType.DIVINATION_CARD)

    def is_complete_set(self):
        return (self.quantity == self.card.max_stack_size)
