from scanf import scanf
import logging
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
    def create_from(trade_request_log):
        logger = logging.getLogger(__name__)
        try:
            trade_request_log = trade_request_log.strip()
            if not trade_request_log:
                return None
            
            trade_request_log = trade_request_log.split("@From ")[1]
            trader = trade_request_log.split(": Hi, I would like to buy your ")[0]

            # Item name
            item_name = trade_request_log.split(" Hi, I would like to buy your ")[1].split(" listed for ")[0]
            trade_request_log = trade_request_log.split(" listed for ")[1]
            
            x = scanf("%d %s in %s (stash tab \"%s\"; position: left %d, top %d)", trade_request_log)
            if not item_name or not x:
                return None

            currency = {'type': x[1], 'amount': x[0]}
            league = x[2]
            stash = x[3]
            position = {'left': x[4], 'top': x[5]}
            return TradeRequest(trader, item_name, currency, league, stash, position)
        except Exception:
            logger.error("Error parsing trade request", exc_info=True)
            return None
    
    def valid(self):
        return True

    def __str__(self):
        return "[{}] trader={}, item_name={}, currency={}, league={}, stash={}, position={}".format(
            self.ts,
            self.trader, 
            self.item_name, 
            json.dumps(self.currency), 
            self.league, 
            self.stash, 
            json.dumps(self.position))