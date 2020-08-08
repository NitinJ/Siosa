import logging
import time

from trade_request import TradeRequest
from trade import TradeInfo, Trade
from client.log_listener import ClientLogListener
from control.mouse_controller import MouseController
from control.keyboard_controller import KeyboardController
from control.window_controller import WindowController
from control.game_controller import GameController
from common.util import *

class TradeController:
    # Maximum time to wait for a player to join hideout.
    HIDEOUT_INVITE_LIFE = 15
    QUEUE_LISTEN_DELAY = 0.05

    def __init__(self, game_controller, log_listener):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.wc = WindowController()

        # Thread 1 for consuming trade log
        self.log_listener = log_listener

        # Controlling all game related stuff.
        self.game_controller = GameController.get_instance()
        
        self.trade_event_queue = self.log_listener.trade_event_queue
        self.hideout_event_queue = self.log_listener.hideout_event_queue

    def start_trading(self):
        self.logger.debug("Starting listening to logs")
        self.log_listener.start()
        self._start_listening_for_incoming_trades()

    def _start_listening_for_incoming_trades(self):
        while True:
            if not self.trade_event_queue.empty():
                trade_request = TradeRequest.create_from(
                    self.trade_event_queue.get())
                self.logger.debug(
                    "Got a trade request : {}".format(trade_request))
                if not trade_request.valid():
                    continue
                trade_info = TradeInfo(trade_request)
                self._start_new_trade(trade_info)
            time.sleep(TradeController.QUEUE_LISTEN_DELAY)

    def _start_new_trade(self, trade_info):
        trader = trade_info.trade_request.trader
        self.logger.debug("Starting new trade with {}".format(trader))
        trade_info.update_status(TradeInfo.Status.STARTING)

        # Invite to hideout
        invite_character_to_party(trader)
        trade_info.update_status(TradeInfo.Status.INVITED)

        # Create trade thread and start.
        trade = Trade(trade_info, self.game_controller)
        trade.start()

        ts1 = time.time()
        self.logger.info("Waiting for {} to join hideout".format(trader))
        while True:
            if time.time() - ts1 > TradeController.HIDEOUT_INVITE_LIFE:
                self.logger.info(
                    "Player failed to join hideout: {}".format(trader))
                trade_info.update_status(TradeInfo.Status.TERMINATED)
                trade.join()
                break

            if self.hideout_event_queue.empty():
                time.sleep(TradeController.QUEUE_LISTEN_DELAY)
                continue

            hideout_event = self.log_listener.hideout_event_queue.get()
            if trade_info.get_player_entered_hideout_message() == hideout_event:
                # Character is in the hideout.
                self.logger.info("Player has joined hideout: {}".format(trader))
                trade_info.update_status(TradeInfo.Status.JOINED)
            elif trade_info.get_player_left_hideout_message() == hideout_event:
                # Character left the hideout
                self.logger.info("Player has left hideout: {}".format(trader))
                trade_info.update_status(TradeInfo.Status.LEFT)
                self.logger.info("Waiting for trade to be over")
                trade.join()
                break
        self.logger.info("Ending trade with: {} with status: {}".format(
            trader, trade_info.status))