import time
from siosa.control.game_step import Step, StepStatus


class TestStep(Step):
    def __init__(self, t:float, fail=False, name="TestStep"):
        """
        Args:
            t: Time to sleep in seconds
        """
        Step.__init__(self)
        self.t = t
        self.fail = fail
        self.name = name

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.logger.debug("Executing {}. Sleeping for {} secs".format(self.name, self.t))
        time.sleep(self.t)
        return StepStatus(self.fail, self.t)

    def __repr__(self):
        return "TestStep({})".format(self.t)
