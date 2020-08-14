from enum import Enum

from siosa.data.poe_item import *
from siosa.network.poe_api import PoeApi


class Currency():
    def __init__(self, ex, name, trade_name, max_stack_in_trade):
        self.exchange = ex
        self.name = name
        self.trade_name = trade_name
        self.max_stack_in_trade = max_stack_in_trade

    def get_value_in_chaos(self):
        return self.exchange.get_exchange_rate(self)

    def __str__(self):
        exchange_rate = self.get_value_in_chaos()
        return "name: {}, trade_name: {}, max_stack: {}, value_in_chaos: {}".format(
            self.name,
            self.trade_name,
            self.max_stack_in_trade,
            exchange_rate if exchange_rate else "unknown")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.name == self.name and other.trade_name == self.trade_name
        return False
