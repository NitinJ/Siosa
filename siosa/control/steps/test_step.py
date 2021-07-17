import time
from siosa.control.game_step import Step, StepStatus


class TestStep(Step):
    def __init__(self, t=""):
        """
        Args:
            t:
        """
        Step.__init__(self)
        self.t = t

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        time.sleep(1)
        return StepStatus(True, self.t)

    def __repr__(self):
        return "TestStep({})".format(self.t)
