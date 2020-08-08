from enum import Enum
import threading
import logging
import time
from control.window_controller import WindowController

class TradeInfo:
    class Status(Enum):
        NOT_STARTED = 'not_started'
        STARTING = 'starting'
        INVITED = 'invited'
        JOINED = 'joined'
        LEFT = 'left'
        TRADING = 'trading'
        TRADE_ACCEPTED = 'trade_accepted'
        TRADE_REJECTED = 'trade_rejected'
        TRADE_COMPLETE = 'trade_complete'
        TERMINATED = 'terminated'

    def __init__(self, trade_request):
        self.logger = logging.getLogger(__name__)
        self.trade_request = trade_request
        self.status = TradeInfo.Status.NOT_STARTED
        self.listeners = []
        self.lock = threading.Lock()

    def get_player_entered_hideout_message(self):
        return "{} has joined the area.".format(self.trade_request.trader)

    def get_status(self):
        self.lock.acquire()
        status = self.status
        self.lock.release()
        return status

    def update_status(self, status):
        self.lock.acquire()
        if status == self.status:
            self.logger.warning(
                "update_status called with same status: {}".format(status))
            self.lock.release()
            return
        old_status = self.status
        self.status = status
        for listener in self.listeners:
            listener.on_trade_status_change(self, old_status, status)
        self.lock.release()

    def register_listener_on_status_change(self, listener):
        self.listeners.append(listener)


class Trade(threading.Thread):
    TRADE_REQUEST_DELAY = 2
    RETRY_REQUEST_DELAY = 3
    MAX_TRADE_RETRIES_ON_REJECT = 1
    MAX_TRADE_TIME_PER_TRY = 20

    def __init__(self,
                 trade_info,
                 game_controller,
                 group=None,
                 target=None,
                 name=None,
                 args=(),
                 kwargs=None,
                 verbose=None):
        super(Trade, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.trade_info = trade_info
        self.wc = WindowController()
        self.trade_info.register_listener_on_status_change(self)
        self.tries = 1
        self.item_sold = False
        self.gc = game_controller

    def on_trade_status_change(self, trade_info, old_status, new_status):
        pass

    def run(self):
        self.logger.info(
            "Starting in-game trade with {}".format(self.trade_info.trade_request.trader))
        self.wc.move_to_poe()
        self._open_stash()
        self._move_item_to_inventory()
        tr = self.trade_info.trade_request
        while True:
            status = self.trade_info.get_status()
            if status in [TradeInfo.Status.TERMINATED, TradeInfo.Status.LEFT]:
                # Player never entered hideout, but might be in party.
                # Player left hideout
                self._kick()
                self._cleanup()
            elif status in [TradeInfo.Status.TRADE_ACCEPTED]:
                # Trade completed
                self._kick(trade_accepted=True)
                self._cleanup()
            elif status in [TradeInfo.Status.TRADE_REJECTED]:
                if self.tries >= Trade.MAX_TRADE_RETRIES_ON_REJECT:
                    self._kick(trade_accepted=False)
                    self._cleanup()
                else:
                    self.tries = self.tries + 1
                    self.trade_info.update_status(TradeInfo.Status.JOINED)
            elif status in [TradeInfo.Status.JOINED]:
                time.sleep(Trade.TRADE_REQUEST_DELAY)
                self._trade()
            elif status == TradeInfo.Status.TRADE_COMPLETE:
                if self.item_sold:
                    self.logger.info(
                        "Trade completed with {}, sold {} for {} {}".format(
                            tr.trader, tr.item_name, tr.currency.amount,
                            tr.currency.type))
                return
            time.sleep(0.05)

    # Cleans up the state, after the player has been kicked from the party.
    def _cleanup(self):
        self.trade_info.update_status(TradeInfo.Status.TRADE_COMPLETE)
        pass

    def _open_stash(self):
        pass

    def _move_item_to_inventory(self):
        pass

    def _trade(self):
        pass

    def _kick(self, trade_accepted=False):
        pass
