from poe_item import *
from enum import Enum

from currency_exchange import CurrencyExchange

class CurrencyType(Enum):
    UNKNOWN = 0
    CHAOS = 1
    EXALT = 2

class Currency:
    def __init__(self, name, max_stack_in_trade):
        self.name = name
        self.max_stack_in_trade = max_stack_in_trade
        self.type = self._get_type()
        self.trade_name = self._get_trade_name()
        self.exchange = CurrencyExchange.get_instance()

    def _get_trade_name(self):
        if self.type == CurrencyType.CHAOS:
            return "chaos"
        else:
            return "exalted"

    def _get_type(self):
        if self.name == "Chaos Orb":
            return CurrencyType.CHAOS
        elif self.name == "Exalted Orb":
            return CurrencyType.EXALT
        raise Exception("Currency not supported !")

    def get_value_in_chaos(self):
        if self.type == CurrencyType.CHAOS:
            return 1
        else:
            return self.exchange.get_exchange_rate(self)

    @staticmethod
    def create(type):
        if type == CurrencyType.CHAOS:
            return Currency("Chaos Orb", 10)
        else:
            return Currency("Exalted Orb", 10)
        raise Exception("Currency not supported !")

    def __str__(self):
        return "{} : {}".format(self.name, self.type)

class CurrencyItem(Item):
    def __init__(self, currency, quantity):
        self.currency = currency
        self.quantity = quantity
        Item.__init__(self, ItemType.CURRENCY)

    def get_value_in_chaos(self):
        return self.currency.get_value_in_chaos() * self.quantity

    def __str__(self):
        return self.currency.__str__() + ", quantity:" + self.quantity
