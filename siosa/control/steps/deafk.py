from siosa.control.game_step import Step, StepStatus


class DeAfkStep(Step):
    def __init__(self):
        Step.__init__(self)

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.cc.console_command("/afkoff")
        return StepStatus(True)
