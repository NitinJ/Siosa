import logging

from siosa.control.game_task import Task
from siosa.control.steps.clean_inventory_step import CleanInventory
from siosa.control.steps.invite_player_to_hideout_step import \
    InvitePlayerToHideoutStep
from siosa.control.steps.open_stash_step import OpenStash
from siosa.control.steps.pickup_item import PickupItem
from siosa.control.steps.place_item_step import PlaceItem
from siosa.control.steps.price_item_step import PriceItem
from siosa.control.steps.scan_inventory_step import ScanInventory
from siosa.control.steps.wait_step import Wait
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.poe_currencies import CurrencyStack, Currency
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_step import TradeStep


class TradeTask(Task):
    def __init__(self, trade_info: TradeInfo, log_listener):
        Task.__init__(self, 10, name='TradeTask')
        self.logger = logging.getLogger(__name__)
        self.info = trade_info
        self.log_listener = log_listener
        self.trade_info = trade_info

    def get_steps(self):
        yield PickupItem(self.trade_info.stash_item)
        ret = self._get_last_step_result()
        if not ret.success:
            return

        yield InvitePlayerToHideoutStep(
            self.trade_info.trade_request.trader,
            msg=TradeTask.get_trade_msg(self.trade_info))
        ret = self._get_last_step_result()
        if not ret.success:
            return

        yield TradeStep(self.trade_info, self.log_listener)
        ret = self._get_last_step_result()
        if ret.success:
            yield Wait(1)
            yield OpenStash()
            yield ScanInventory()
            yield CleanInventory()
            return

        # Place item back to the stash where it belongs and list it again.
        stash_index = self.trade_info.stash_item.stash_tab.index
        stash_cell = self.trade_info.stash_item.position
        yield PlaceItem(stash_index, stash_cell, (0, 0))
        yield PriceItem(stash_index, stash_cell,
                        TradeTask.get_currency_stack_from_trade_info(
                            self.trade_info))

    @staticmethod
    def get_currency_stack_from_trade_info(trade_info):
        type = trade_info.trade_request.currency['type']
        amount = trade_info.trade_request.currency['amount']
        currency = Currency(CurrencyExchange(), 'Unknown', type, 10)
        return CurrencyStack(currency, amount)

    @staticmethod
    def get_trade_msg(trade_info: TradeInfo):
        return "Ready to be picked up: [{}], for [{} {}]".format(
            trade_info.trade_request.item_name,
            trade_info.trade_request.currency['type'],
            trade_info.trade_request.currency['amount'])
