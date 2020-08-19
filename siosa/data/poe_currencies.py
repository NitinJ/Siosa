from enum import Enum
import logging

from siosa.data.poe_item import *
from siosa.network.poe_api import PoeApi
from siosa.data.static_data import StaticData
from siosa.data.currency_exchange import CurrencyExchange


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

    @staticmethod
    def create(name=None, trade_name=None, max_stack_in_trade=10):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        if not name and not trade_name:
            logger.warning("Cannot create currency as both name and trade_name \
                are null")
            return None
        sd = StaticData()
        
        if not name:
            name = sd.get_name_for_trade_id(trade_name)
            if not name:
                logger.warning("Cannot create currency as name for trade_name={} is null".format(trade_name)) 
                return None
        elif not trade_name:
            trade_name = sd.get_trade_id_for_name(name)
            if not trade_name:
                logger.warning("Cannot create currency as trade_name for name={} is null".format(name)) 
                return None
        
        return Currency(CurrencyExchange(), name, trade_name, max_stack_in_trade)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.name == self.name and other.trade_name == self.trade_name
        return False


class CurrencyStack(Item):
    def __init__(self, currency, quantity,  item_type=ItemType.CURRENCY, item_info={}):
        self.currency = currency
        self.quantity = quantity
        info = {
            'rarity': 'Currency',
            'type_line': currency.name,
            'stack_size': quantity,
            'max_stack_size': currency.max_stack_in_trade
        }
        item_info.update(info)
        Item.__init__(self, item_info=item_info, item_type=item_type)

    def is_partial(self):
        return (not self.quantity.is_integer())

    def get_total_value_in_chaos(self):
        return math.floor(self.currency.get_value_in_chaos() * self.quantity)
