import time


class TradeBlacklist:
    ONE_YEAR = 31536000
    ONE_MINUTE = 60

    def __init__(self, backup_interval=ONE_MINUTE):
        """
        Args:
            backup_interval:
        """
        self.blacklist = {}
        self.backup_interval = backup_interval

    def is_blacklisted(self, trader):
        """
        Args:
            trader:
        """
        if trader not in self.blacklist.keys():
            return False
        if self.blacklist[trader]['expires'] <= time.time():
            self.remove(trader)
            return True
        return False

    def add(self, trader, duration=ONE_YEAR):
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
        if self.is_blacklisted(trader):
            self.blacklist.pop(trader)
