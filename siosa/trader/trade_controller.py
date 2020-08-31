import logging
import time

from siosa.control.game_controller import GameController
from siosa.control.trade_task import TradeTask
from siosa.data.stash import Stash
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_request import TradeRequest


class TradeController:
    QUEUE_LISTEN_DELAY = 0.05

    def __init__(self, game_controller, log_listener):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        # Thread 1 for consuming trade log
        self.log_listener = log_listener
        self.trade_event_queue = self.log_listener.trade_event_queue

        # Controlling all game related stuff.
        self.game_controller = GameController()

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
        self.game_controller.submit_task(TradeTask(trade_info))

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
        valid = True
        trade_info = None

        stash = Stash()
        candidate_stash_tabs = stash.get_stash_tabs_by_name(
            trade_request.stash)
        if not candidate_stash_tabs:
            return None

        item, stash_tab = self._get_item_from_candidate_stash_tabs(
            candidate_stash_tabs, trade_request)
        if not item or not self._is_item_valid(item):
            return None

        return TradeInfo(trade_request, stash_tab, item)

    def _is_item_valid(self, item):
        # TODO: Fill this up.
        return True

    def _get_item_from_candidate_stash_tabs(self, candidate_stash_tabs, trade_request):
        for stash_tab in candidate_stash_tabs:
            x = trade_request.position['x']
            y = trade_request.position['y']
            # x,y are 1 indexed
            item_at_location = stash_tab.get_item_at_location(x - 1, y - 1)
            if item_at_location and item_at_location.get_full_name() == trade_request.item_name:
                return item_at_location, stash_tab
        return None, None
