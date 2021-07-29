import logging

from siosa.control.game_state import GameState
from siosa.control.game_task import Task
from siosa.control.steps.test_step import TestStep


class TestTask(Task):
    def __init__(self, priority, sleep_time=1.0, name="TestTask"):
        """
        Args:
            priority:
        """
        self.logger = logging.getLogger(__name__)
        Task.__init__(self, priority, name=__name__)
        self.sleep_time = sleep_time
        self.name = name

    def get_steps(self):
        """Generator function for step execution logic. Returns: A generator
        function for steps.
        """
        yield TestStep(
            self.sleep_time,
            fail=False,
            name='{}: TestStep({})'.format(self.name, 1))
        return True


if __name__ == "__main__":
    t = TestTask(11)
    t.run_task(GameState())
