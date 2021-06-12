import logging

from siosa.control.game_task import Task
from siosa.control.steps.clean_inventory_step import CleanInventory
from siosa.control.steps.test_step import TestStep


class TestTask(Task):
    def __init__(self, priority, steps=()):
        self.logger = logging.getLogger(__name__)
        self.steps = [TestStep()] if not steps else list(steps)
        Task.__init__(self, priority, self.steps, name=__name__)

    def _resume_internal(self):
        pass

    def _cleanup_internal(self):
        pass

    def get_steps(self):
        return self.steps
