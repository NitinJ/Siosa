import logging 
from scanf import scanf 

class TradeEvent:
    def __init__(self, raw_event, trader, item_name, currency, league, stash, position):
        self.logger = logging.getLogger(__name__)
        self.raw_event = raw_event
        self.trader = trader
        self.item_name = item_name
        self.currency = currency
        self.league = league
        self.stash = stash
        self.position = position

    @staticmethod
    def create(log_line):
        event_str = "Hi, I would like to buy your"
        from_str = "@From"
        is_pass = log_line.find(event_str) > -1 and log_line.find(from_str) > -1
        if not is_pass:
            return None
        try:
            log_line = log_line.strip()
            if not log_line:
                return None
            log_line = log_line.split("@From ")[1]
            raw_event = "@From " + log_line
            trader = log_line.split(": Hi, I would like to buy your ")[0]

            # Item name
            item_name = log_line.split(" Hi, I would like to buy your ")[1].split(" listed for ")[0]
            log_line = log_line.split(" listed for ")[1]
            
            x = scanf("%d %s in %s (stash tab \"%s\"; position: left %d, top %d)", log_line)
            if not item_name or not x:
                return None

            currency = {'type': x[1], 'amount': x[0]}
            league = x[2]
            stash = x[3]
            position = {'left': x[4], 'top': x[5]}
            return TradeEvent(raw_event, trader, item_name, currency, league, stash, position)
        except Exception:
            # self.logger.error("Error parsing log_line for trade request", exc_info=True)
            return None