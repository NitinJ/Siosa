import logging
import math
import re


class TradeEvent:
    REGX = re.compile(
        '(\d*\.?\d*) (?s)(.*) in (?s)(.*) \(stash tab "(?s)(.*)"; position: left ([-+]?\d+), top ([-+]?\d+)\)')

    def __init__(self, raw_event, trader, item_name, currency, league, stash, position):
        self.logger = logging.getLogger(__name__)
        self.raw_event = raw_event
        self.trader = trader
        self.item_name = item_name
        self.currency = currency
        self.league = league
        self.stash = stash
        self.position = position

    def __str__(self):
        return str({
            'trader': self.trader,
            'item_name': self.item_name,
            'currency': self.currency,
            'league': self.league,
            'stash': self.stash,
            'position': self.position,
        })

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
            if not trader:
                return None
            trader = trader.split(" ")[-1]

            # Item name
            item_name = log_line.split(" Hi, I would like to buy your ")[1].split(" listed for ")[0]
            if not item_name:
                return None
            log_line = log_line.split(" listed for ")[1]

            x = TradeEvent.REGX.match(log_line).groups()
            if not x:
                return None

            currency = {'type': x[1], 'amount': float(x[0])}
            league = x[2]
            stash = x[3]
            position = (int(x[4]) - 1, int(x[5]) - 1)

            if position[0] < 0 or position[1] < 0:
                return None
            if currency['amount'] <= 0:
                return None
            if not league or not stash:
                return None

            return TradeEvent(raw_event, trader, item_name, currency, league, stash, position)
        except Exception:
            return None


if __name__ == "__main__":
    te = TradeEvent.create('@From <[KREK]> Corpz: Hi, I would like to buy your Rapture Ruin Medium Cluster Jewel listed for 3.5 exalted in Ritual (stash tab "SELL"; position: left 4, top 9)')
    assert te.trader == "Corpz"
    assert te.item_name == "Rapture Ruin Medium Cluster Jewel"
    assert te.currency['type'] == "exalted"
    assert math.isclose(te.currency['amount'], 3.5)
    assert te.league == "Ritual"
    assert te.stash == "SELL"
    assert te.position == (3, 8)

    te = TradeEvent.create('@From PiercerCC: Hi, I would like to buy your level 19 0% Physical to Lightning Support listed for 2 chaos in Ritual (stash tab "~price 2 chaos"; position: left 1, top 11)')
    print(te)
