import logging
import time

from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_controller import GameController
from siosa.data.stash import Stash
from siosa.data.stash_item import StashItem
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_request import TradeRequest
from siosa.trader.trade_task import TradeTask


class TradeController:
    QUEUE_LISTEN_DELAY = 0.05

    def __init__(self, game_controller: GameController, log_listener, config: SiosaConfig):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.config = config

        # Thread 1 for consuming trade log
        self.log_listener = log_listener
        self.trade_event_queue = self.log_listener.trade_event_queue

        # Controlling all game related stuff.
        self.game_controller = game_controller

    def start_trading(self):
        self.logger.debug("Starting listening to logs")
        self._start_listening_for_incoming_trades()

    def _start_listening_for_incoming_trades(self):
        while True:
            if not self.trade_event_queue.empty():
                trade_request = TradeRequest.create_from(
                    self.trade_event_queue.get())
                self.logger.debug(
                    "Got a trade request : {}".format(trade_request))
                trade_info = self._validate_trade_request(trade_request)
                self.logger.debug("TradeRequest is {}".format(
                    "Valid" if trade_info else "Invalid"))
                if not trade_info:
                    continue
                self._start_new_trade(trade_info)
            time.sleep(TradeController.QUEUE_LISTEN_DELAY)

    def _start_new_trade(self, trade_info):
        self.logger.debug("Starting new trade with {}".format(
            trade_info.trade_request.trader))
        self.game_controller.submit_task(TradeTask(trade_info, self.log_listener))

    def _validate_trade_request(self, trade_request):
        """Validates a trade request object and returns a trade_info object if
        validated. Verifies that -
        1. Trader isn't blacklisted.
        2. Basic sanity checks on stash index and item indexes are passing.
        3. Currency is allowed for trade.
        4. League is allowed for trade.

        Args:
            trade_request (TradeRequest): The trade request object

        Returns:
            boolean, TradeInfo: Whether the trade request is valid or not
            followed by the trade_info object.
        """
        stash = Stash()

        candidate_stash_tabs = stash.get_stash_tabs_by_name(
            trade_request.stash)
        if not candidate_stash_tabs:
            self.logger.debug("TradeRequest invalid: Couldn't find "
                              "candidate stash tabs for the item.")
            return None

        stash_item = self._get_item_from_candidate_stash_tabs(
            candidate_stash_tabs, trade_request)

        if not stash_item:
            self.logger.debug("TradeRequest invalid: Couldn't find "
                              "item in stash tabs.")
            return None
        if not self._is_item_valid(stash_item):
            self.logger.debug("TradeRequest invalid: Item isn't valid.")
            return None

        # Hack to ensure that we only sell from a fixed tab defined in config
        # by sell_index.
        # TODO: Remove this check when we are able to sell from any stash.
        if stash_item.stash_tab.index not in self.config.get_sell_tab_index():
            self.logger.debug("TradeRequest invalid: Trade not from "
                              "allowed stash tab.")
            return None

        return TradeInfo(trade_request, stash_item)

    def _is_item_valid(self, stash_item):
        # TODO: Fill this up.
        return True

    def _get_item_from_candidate_stash_tabs(self, candidate_stash_tabs, trade_request):
        for stash_tab in candidate_stash_tabs:
            x = trade_request.position[0]
            y = trade_request.position[1]
            item_at_location = stash_tab.get_item_at_location(x, y)
            if item_at_location and item_at_location.get_full_name() == trade_request.item_name:
                return StashItem(item_at_location, stash_tab, (x, y))
        return None
