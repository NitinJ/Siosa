import logging
import time

from siosa.control.game_task import Task
from siosa.control.steps.scan_inventory_step import ScanInventory
from siosa.control.steps.clean_inventory_step import CleanInventory


class TestTask(Task):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.steps = TestTask.get_steps()
        Task.__init__(self, 10, self.steps, name=__name__)

    def cleanup(self):
        pass

    def resume(self, game_state):
        self.game_state = game_state
        pass

    @staticmethod
    def get_steps():
        return [CleanInventory()]