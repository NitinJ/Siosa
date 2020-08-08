import threading
import time
import json
import math
import logging

from common.singleton import Singleton
from network.poe_api import PoeApi

REFRESH_DURATION = 10 * 60

class CurrencyExchange(Singleton):
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
        self.logger.info("Updating currency rates {}".format(json.dumps(rates)))
        self.exchange_rate_in_chaos = rates
        self.lock.release()

    def get_exchange_rate(self, currency):
        self.lock.acquire()
        if currency.trade_name not in self.exchange_rate_in_chaos.keys():
            self.lock.release()
            return None
        rate = self.exchange_rate_in_chaos[currency.trade_name]
        self.lock.release()
        return rate

class Exchanger(threading.Thread):
    def __init__(self, poe_api, exchange, args=()):
        super(Exchanger, self).__init__()
        self.api = poe_api
        self.exchange = exchange
    
    def run(self):
        while True:
            self.exchange.update_rates({
                'exalted': int(math.floor(
                    self.api.get_exchange_rate("exalted", "chaos")))
            })
            time.sleep(REFRESH_DURATION)
