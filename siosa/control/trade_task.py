import logging
import time

from siosa.control.game_step import OpenStash
from siosa.control.game_task import Task


class TradeTask(Task):
    def __init__(self, game_state, trade_request):
        self.logger = logging.getLogger(__name__)
        self.req = trade_request
        self.steps = TradeTask.get_steps(trade_request)
        Task.__init__(self, game_state, 10, self.steps)

    def cleanup(self):
        pass

    def resume(self):
        pass

    @staticmethod
    def get_steps(trade_request):
        return [OpenStash(self.game_state)]
