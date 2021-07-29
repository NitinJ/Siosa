import logging

from siosa.control.game_task import Task
from siosa.control.steps.deafk import DeAfkStep


class DeAfkTask(Task):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        Task.__init__(self, 9, name='DeAfkTask')

    def get_steps(self):
        return (
            DeAfkStep(),
        )
