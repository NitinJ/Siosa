import logging
import time

from siosa.common.decorations import override
from siosa.common.stoppable_thread import StoppableThread
from siosa.config.siosa_config import SiosaConfig
from siosa.control.deafk_task import DeAfkTask
from siosa.control.game_controller import GameController
from siosa.data.stash import Stash
from siosa.data.stash_item import StashItem
from siosa.trader.trade_blacklist import TradeBlacklist
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_request import TradeRequest
from siosa.trader.trade_task import TradeTask


class TradeController(StoppableThread):
    QUEUE_LISTEN_DELAY = 0.05
    AFK_TIME = 10 * 60  # 10 mins
    MAX_BACKLOG_TIME = 60  # 1 minute

    def __init__(self, game_controller: GameController, log_listener,
                 config: SiosaConfig):
        """
        Args:
            game_controller (GameController):
            log_listener:
            config (SiosaConfig):
        """
        StoppableThread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.config = config

        # Thread 1 for consuming trade log
        self.log_listener = log_listener
        self.trade_event_queue = self.log_listener.trade_event_queue

        # Controlling all game related stuff.
        self.game_controller = game_controller
        self.last_afk_ts = time.time()

        # Trade blacklist.
        self.trade_blacklist = TradeBlacklist()

    @override
    def start(self):
        self.logger.debug("Starting listening to incoming trades")
        super().start()

    @override
    def run_once(self):
        if time.time() - self.last_afk_ts > TradeController.AFK_TIME:
            self.game_controller.submit_task(DeAfkTask())
            self.last_afk_ts = time.time()

        if not self.trade_event_queue.empty():
            trade_request = TradeRequest.create_from(
                self.trade_event_queue.get())
            self.logger.debug("Got a trade request : {}".format(trade_request))
            trade_info = self._validate_trade_request(trade_request)
            self.logger.debug("TradeRequest is {}".format(
                "Valid" if trade_info else "Invalid"))
            if not trade_info:
                return
            self.trade_blacklist.add(trade_request.trader)
            self._start_new_trade(trade_info)
        time.sleep(TradeController.QUEUE_LISTEN_DELAY)

    def _start_new_trade(self, trade_info):
        """
        Args:
            trade_info:
        """
        self.logger.debug("Starting new trade with {}".format(
            trade_info.trade_request))
        self.game_controller.submit_task(
            TradeTask(trade_info, self.log_listener))

    def _validate_trade_request(self, trade_request):
        """Validates a trade request object and returns a trade_info object if
        validated. Verifies that - 1. Trader isn't blacklisted. 2. Basic sanity
        checks on stash index and item indexes are passing. 3. Currency is
        allowed for trade. 4. League is allowed for trade.

        Args:
            trade_request (TradeRequest): The trade request object

        Returns:
            boolean, TradeInfo: Whether the trade request is valid or not
            followed by the trade_info object.
        """
        if time.time() - trade_request.request_time > \
                TradeController.MAX_BACKLOG_TIME:
            self.logger.debug(
                "Trade request backlog time exceeded : {}".format(
                    trade_request))
            return None
        if self.trade_blacklist.is_blacklisted(trade_request.trader):
            self.logger.debug(
                "Trader is blacklisted : {}".format(trade_request))
            return None

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
                              "item in stash tabs. Trying to refresh stash.")
            stash.refresh()
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
        """
        Args:
            stash_item:
        """
        return True

    def _get_item_from_candidate_stash_tabs(self, candidate_stash_tabs,
                                            trade_request):
        """
        Args:
            candidate_stash_tabs:
            trade_request:
        """
        self.logger.debug(
            "Checking item ({}) in candidate stash tabs: {}".format(
                (trade_request.position[0], trade_request.position[1]),
                candidate_stash_tabs))

        for stash_tab in candidate_stash_tabs:
            # These positions are 0 indexed but still are x,y and not row,col.
            x = trade_request.position[0]
            y = trade_request.position[1]

            item_at_location = stash_tab.get_item_at_location(x, y)
            if item_at_location and \
                    item_at_location.get_trade_name().lower() == \
                    trade_request.item_name.lower():
                # Use y,x for position instead of x,y as x:Left, y:Top
                return StashItem(item_at_location, stash_tab, (y, x))
        return None
