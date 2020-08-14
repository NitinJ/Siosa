import json
import logging
import math
import threading
import time

from siosa.common.singleton import Singleton
from siosa.data.poe_currencies import Currency
from siosa.network.poe_api import PoeApi

REFRESH_DURATION = 10 * 60


class CurrencyExchange(Singleton):
    currency_data = None

    def __init__(self, poe_api):
        super(CurrencyExchange, self).__init__()

        self.logger = logging.getLogger()
        self.exchange_rate_in_chaos = {}
        self.poe_api = poe_api
        self.lock = threading.Lock()

        self.exchanger = Exchanger(self.poe_api, self)
        self.exchanger.start()

        self.update_rates({
            'exalted': int(math.floor(
                self.poe_api.get_exchange_rate("exalted", "chaos")))
        })

    def update_rates(self, rates):
        self.lock.acquire()
        self.logger.info(
            "Updating currency rates {}".format(json.dumps(rates)))
        self.exchange_rate_in_chaos = rates
        self.lock.release()

    # Currently only supports exalted->chaos
    def get_exchange_rate(self, currency):
        self.lock.acquire()
        if currency.trade_name not in self.exchange_rate_in_chaos.keys():
            self.lock.release()
            return None
        rate = self.exchange_rate_in_chaos[currency.trade_name]
        self.lock.release()
        return rate

    def create_currency(self, name=None, trade_name=None, stack_max_size=10):
        if not name and not trade_name:
            self.logger.error("Invalid currency with both name and trade_name=None")
            return None
        data = self._get_static_currency_data()
        if name not in data.keys():
            return None
        name = name if name else self.get_currency_name_for_trade_name(trade_name) 
        trade_name = trade_name if trade_name else self.get_trade_name_for_currency_name(name)
        return Currency(self, name, trade_name, stack_max_size)

    def _get_static_currency_data(self):
        if CurrencyExchange.currency_data:
            return CurrencyExchange.currency_data
        static_data = self.poe_api.get_static_data()
        data = {}
        for entry in static_data:
            if entry and entry['id'] == 'Currency':
                for currency in entry['entries']:
                    name = currency['text']
                    trade_name = currency['id']
                    data[name] = trade_name
                break
        CurrencyExchange.currency_data = data
        return data

    def get_trade_name_for_currency_name(self, currency_name):
        data = self._get_static_currency_data()
        if currency_name not in data.keys():
            return None
        return data[currency_name]

    def get_currency_name_for_trade_name(self, trade_name):
        data = self._get_static_currency_data()
        for k, v in data.items():
            if v == trade_name:
                return k
        return None


class Exchanger(threading.Thread):
    def __init__(self, poe_api, exchange, args=()):
        super(Exchanger, self).__init__()
        self.api = poe_api
        self.exchange = exchange

    def run(self):
        while True:
            time.sleep(REFRESH_DURATION)
            self.exchange.update_rates({
                'exalted': int(math.floor(
                    self.api.get_exchange_rate("exalted", "chaos")))
            })
