import logging

from siosa.control.game_task import Task
from siosa.control.steps.clean_inventory_step import CleanInventory
from siosa.control.steps.invite_player_to_hideout_step import \
    InvitePlayerToHideoutStep
from siosa.control.steps.open_stash_step import OpenStash
from siosa.control.steps.pickup_item import PickupItem
from siosa.control.steps.scan_inventory_step import ScanInventory
from siosa.control.steps.wait_step import Wait
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_step import TradeStep


class TradeTask(Task):
    def _resume_internal(self):
        pass

    def _cleanup_internal(self):
        pass

    def __init__(self, trade_info, log_listener):
        Task.__init__(self, 10, name='TradeTask')
        self.logger = logging.getLogger(__name__)
        self.info = trade_info
        self.log_listener = log_listener
        self.trade_info = trade_info

    def get_steps(self):
        return [
            PickupItem(self.trade_info.stash_item),
            InvitePlayerToHideoutStep(
                self.trade_info.trade_request.trader,
                msg=TradeTask.get_trade_msg(self.trade_info)),
            TradeStep(self.trade_info, self.log_listener),
            Wait(1),
            OpenStash(),
            ScanInventory(),
            CleanInventory()
        ]

    @staticmethod
    def get_trade_msg(trade_info: TradeInfo):
        return "Ready to be picked up: [{}], for [{} {}]".format(
            trade_info.trade_request.item_name,
            trade_info.trade_request.currency['type'],
            trade_info.trade_request.currency['amount'])
