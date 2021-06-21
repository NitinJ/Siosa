import logging

from siosa.control.game_state import GameState
from siosa.control.game_task import Task
from siosa.control.steps.test_step import TestStep


class TestTask(Task):
    def __init__(self, priority):
        self.logger = logging.getLogger(__name__)
        Task.__init__(self, priority, name=__name__)

    def get_steps(self):
        """
        Generator function for step execution logic.
        Returns: A generator function for steps.
        """
        yield TestStep(2)
        if self._get_last_step_execution_status().info == 1:
            yield TestStep(2)
        else:
            yield TestStep(3)


if __name__ == "__main__":
    t = TestTask(10)
    t.run_task(GameState())
