from siosa.control.game_step import Step, StepStatus


class SwitchToGame(Step):
    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        if not self.wc.is_poe_in_foreground():
            self.wc.move_to_poe()
        return StepStatus(True)
