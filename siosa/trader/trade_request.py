import json
import time


class TradeRequest:
    def __init__(self, trader, item_name, currency, league, stash, position):
        self.trader = trader
        self.item_name = item_name
        self.currency = currency
        self.league = league
        self.stash = stash
        self.position = position
        self.ts = time.time()

    @staticmethod
    def create_from(trade_event):
        return TradeRequest(
            trade_event.trader,
            trade_event.item_name,
            trade_event.currency,
            trade_event.league,
            trade_event.stash,
            trade_event.position)

    def __str__(self):
        return "[{}] trader={}, item_name={}, currency={}, league={}, stash={}, position={}".format(
            self.ts,
            self.trader,
            self.item_name,
            json.dumps(self.currency),
            self.league,
            self.stash,
            json.dumps(self.position))
