from siosa.control.game_step import Step


class SwitchToGame(Step):
    def execute(self, game_state):
        self.logger.info("Executing step: SwitchToGame")
        if not self.wc.is_poe_in_foreground():
            self.wc.move_to_poe()
