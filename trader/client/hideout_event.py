from scanf import scanf

class HideoutEvent:
    def __init__(self, player):
        self.player = player

    @staticmethod
    def create(log_line):
        is_pass = log_line.find("has joined the area") > -1
        if not is_pass:
            return None
        hideout_event = log_line.strip().split("3020] : ")[1][:-1]
        player = scanf("%s has joined the area.", hideout_event)
        if player:
            return HideoutEvent(player)
        return None
