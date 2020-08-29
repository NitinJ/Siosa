import logging
import time

from siosa.control.game_task import Task


class TradeTask(Task):
    def __init__(self, trade_info):
        self.logger = logging.getLogger(__name__)
        self.info = trade_info
        self.steps = TradeTask.get_steps(self.info)
        Task.__init__(self, 10, self.steps)

    def cleanup(self):
        pass

    def resume(self, game_state):
        self.game_state = game_state
        pass

    @staticmethod
    def get_steps(trade_request):
        return []


'''
class Trade(threading.Thread):
    TRADE_REQUEST_DELAY = 2
    RETRY_REQUEST_DELAY = 3
        # Maximum time to wait for a player to join hideout.
    HIDEOUT_INVITE_LIFE = 15
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
'''