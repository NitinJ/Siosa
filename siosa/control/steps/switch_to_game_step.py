from control.game_step import Step

class SwitchToGame(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
    
    def execute(self):
        self.logger.info("Executing step: SwitchToGame")
        if not self.wc.is_poe_in_foreground():
            self.wc.move_to_poe()
