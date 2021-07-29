import time


class TradeBlacklist:
    ONE_MINUTE = 60

    def __init__(self):
        self.blacklist = {}

    def is_blacklisted(self, trader):
        """
        Args:
            trader:
        """
        if trader not in self.blacklist.keys():
            return False

        if time.time() > self.blacklist[trader]['expires']:
            self.remove(trader)
            return False

        return True

    def add(self, trader, duration=ONE_MINUTE):
        """
        Args:
            trader:
            duration:
        """
        t = time.time()
        self.blacklist[trader] = {'ts': t, 'expires': t + duration}

    def remove(self, trader):
        """
        Args:
            trader:
        """
        if trader in self.blacklist.keys():
            self.blacklist.pop(trader)
