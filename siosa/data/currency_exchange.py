import json
import logging
import math
import threading
import time

from siosa.common.singleton import Singleton

REFRESH_DURATION = 10 * 60


class CurrencyExchange(metaclass=Singleton):
    currency_data = None

    def __init__(self, poe_api):
        """
        Args:
            poe_api:
        """
        super(CurrencyExchange, self).__init__()

        self.logger = logging.getLogger()
        self.exchange_rate_in_chaos = {}
        self.poe_api = poe_api
        # self.other_currencies_data = {}

        self.lock = threading.Lock()
        self.exchanger = Exchanger(self.poe_api, self)
        self.exchanger.start()

        rate = self.poe_api.get_exchange_rate("exalted", "chaos")
        if rate:
            self.update_rates({
                'exalted': int(math.floor(rate))
            })

    def update_rates(self, rates):
        """
        Args:
            rates:
        """
        self.lock.acquire()
        self.logger.info(
            "Updating currency rates {}".format(json.dumps(rates)))
        self.exchange_rate_in_chaos = rates
        self.lock.release()

    # Currently only supports exalted->chaos
    def get_exchange_rate(self, currency):
        """
        Args:
            currency:
        """
        self.lock.acquire()
        if currency.trade_name not in self.exchange_rate_in_chaos.keys():
            self.lock.release()
            return None
        rate = self.exchange_rate_in_chaos[currency.trade_name]
        self.lock.release()
        return rate


class Exchanger(threading.Thread):
    def __init__(self, poe_api, exchange, args=()):
        """
        Args:
            poe_api:
            exchange:
            args:
        """
        super(Exchanger, self).__init__()
        self.api = poe_api
        self.exchange = exchange

    def run(self):
        while True:
            time.sleep(REFRESH_DURATION)
            rate = self.api.get_exchange_rate("exalted", "chaos")
            if not rate:
                continue
            self.exchange.update_rates({
                'exalted': int(math.floor(rate))
            })
