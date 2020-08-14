from scanf import scanf

class HideoutEvent:
    def __init__(self, player, joined):
        self.player = player
        self.joined = joined

    @staticmethod
    def create(log_line):
        if log_line.find("has joined the area") > -1:
            hideout_event = log_line.strip().split(" : ")[1][:-1]
            player = scanf("%s has joined the area.", hideout_event)
            return HideoutEvent(player, joined=True)
        elif log_line.find("has left the area") > -1:
            hideout_event = log_line.strip().split(" : ")[1][:-1]
            player = scanf("%s has left the area.", hideout_event)
            return HideoutEvent(player, joined=True)
        else:
            return None