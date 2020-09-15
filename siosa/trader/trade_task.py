import logging

from siosa.control.game_task import Task
from siosa.control.steps.clean_inventory_step import CleanInventory
from siosa.control.steps.invite_player_to_hideout_step import \
    InvitePlayerToHideoutStep
from siosa.control.steps.pickup_item import PickupItem
from siosa.trader.trade_step import TradeStep


class TradeTask(Task):
    def _resume_internal(self):
        pass

    def _cleanup_internal(self):
        pass

    def __init__(self, trade_info, log_listener):
        Task.__init__(self, 10, self.steps, name='TradeTask')
        self.logger = logging.getLogger(__name__)
        self.info = trade_info
        self.log_listener = log_listener
        self.steps = TradeTask.steps(self.info, log_listener)

    @staticmethod
    def steps(trade_info, log_listener):
        return [
            PickupItem(trade_info.stash_item),
            InvitePlayerToHideoutStep(trade_info.trade_request.trader),
            TradeStep(trade_info, log_listener),
            CleanInventory()
        ]