class TradeEvent:
    def __init__(self):
        pass

    @staticmethod
    def create(log_line):
        event_str = "Hi, I would like to buy your"
        from_str = "@From"
        is_pass = log_line.find(event_str) > -1 and log_line.find(from_str) > -1
        if not is_pass:
            return None
        data = {}