class TradeStatusEvent:
    def __init__(self, status):
        self.status = status

    def accepted(self):
        return self.status == 0

    @staticmethod
    def create(log_line):
        cancelled = log_line.find("Trade cancelled")
        accepted = log_line.find("Trade accepted")
        if accepted == -1 and cancelled == -1:
            return None
        elif accepted > -1:
            return TradeStatusEvent(0)
        else:
            return TradeStatusEvent(1)
