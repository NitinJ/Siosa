import asyncio
import time

from siosa.control.console_controller import Commands
from siosa.control.game_step import Step, StepStatus
from siosa.dfa.dfa_asyncio import DfaAsyncio
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry

from siosa.location.location_factory import LocationFactory, Locations
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_state import States, TradeState
from siosa.trader.trade_state_updater import TradeStateUpdater
from siosa.trader.trade_verifier import TradeVerifier


class TradeStep(Step):
    UPDATE_INTERVAL = 0.01
    MAX_RETRIES = 2
    TRADE_THANK_YOU = "Thanks and have fun !"
    TRADE_OFFER_WAIT_TIMEOUT = 20
    TRADE_ACCEPT_WAIT_TIMEOUT = 10
    RETRY_TIMEOUT = 2
    TRADE_REQUEST_SEND_DELAY = 2

    def __init__(self, trade_info: TradeInfo, log_listener):
        """
        Args:
            trade_info (TradeInfo):
            log_listener:
        """
        super().__init__()
        self.trade_info = trade_info
        self.trader = self.trade_info.trade_request.trader
        self.lf = LocationFactory()
        self.state_updater = None
        self.log_listener = log_listener

        # Template matchers.
        self.inventory_tm = \
            TemplateMatcher(TemplateRegistry.INVENTORY_BANNER.get())
        self.trade_window_tm = \
            TemplateMatcher(TemplateRegistry.TRADE_WINDOW_CLOSE_BUTTON.get())

        # Current trade state, end states and dfa initialization.
        self.state = TradeState(States.NOT_STARTED)
        self.updater_end_states = [
            States.ACCEPTED,
            States.LEFT,
            States.ENDED
        ]
        self.dfa = DfaAsyncio(self.state, TradeState(States.ENDED))
        self._initialize_state_transitions()

        # Trade state variables.
        self.retries = TradeStep.MAX_RETRIES
        self.accepted = False
        self.trade_verifier = TradeVerifier(trade_info.trade_request)

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state
        self.state_updater = TradeStateUpdater(
            game_state, self.state, self.trade_info, self.log_listener)

        self.dfa.start()
        while not self._updater_end_state_reached():
            self.state_updater.update()
            time.sleep(TradeStep.UPDATE_INTERVAL)
        self.dfa.join()
        self.on_end()
        return StepStatus(self.accepted)

    def _update_trade_state(self):
        pass

    def _initialize_state_transitions(self):
        self.dfa.add_state_fn(TradeState(States.NOT_STARTED),
                              self.send_trade_request)
        self.dfa.add_state_fn(TradeState(States.ACCEPTED), self.on_accept)
        self.dfa.add_state_fn(TradeState(States.CANCELLED), self.on_cancel)
        self.dfa.add_state_fn(TradeState(States.LEFT), self.on_left)

        # Trading states.
        offer_timeout = TradeStep.TRADE_OFFER_WAIT_TIMEOUT
        accept_timeout = TradeStep.TRADE_ACCEPT_WAIT_TIMEOUT

        # Not-offered
        self.dfa.add_state_fn(TradeState(States.TRADING_NO_NO), self.offer)
        self.dfa.add_state_fn(TradeState(States.TRADING_NO_O), self.offer)
        self.dfa.add_state_fn(TradeState(States.TRADING_NO_A), self.offer)

        # Offered
        self.dfa.add_state_fn(TradeState(States.TRADING_O_NO),
                              self.cancel(offer_timeout))
        self.dfa.add_state_fn(TradeState(States.TRADING_O_O),
                              self.cancel(accept_timeout))
        self.dfa.add_state_fn(TradeState(States.TRADING_O_R), self.verify)
        self.dfa.add_state_fn(TradeState(States.TRADING_O_A), self.verify)

        # Verified success
        self.dfa.add_state_fn(TradeState(States.TRADING_VS_A), self.accept)

        # Verified fail
        self.dfa.add_state_fn(TradeState(States.TRADING_VF_A),
                              self.cancel_with_message(""))

    def transition(self, state_value):
        """
        Args:
            state_value:
        """
        async def wrapper():
            self.state.update(state_value)
        return wrapper

    def cancel_with_message(self, message):
        """
        Args:
            message:
        """
        async def wrapper():
            self.kc.keypress('Esc')
            self.cc.send_chat(self.trader, message)
            self.state.update(States.CANCELLED)
        return wrapper

    def cancel(self, timeout):
        """
        Args:
            timeout:
        """
        async def wrapper():
            await asyncio.sleep(timeout)
            self.kc.keypress('Esc')
            self.state.update(States.CANCELLED)
        return wrapper

    def _updater_end_state_reached(self):
        for end_state in self.updater_end_states:
            if self.state.equals(end_state):
                self.logger.debug("End state reached for updater.")
                return True
        return False

    def on_end(self):
        self.logger.debug("Trade ended.")
        self._kick_from_party()

    async def verify(self):
        self.logger.debug("Verifying trade".format(self.trader))
        res = self.trade_verifier.verify()
        if res.is_verified():
            self.state.update_me('VERIFIED_SUCCESS')
        else:
            self.state.update_me('VERIFIED_FAIL')
            self.cc.send_chat(self.trader, res.get_msg())

    async def accept(self):
        self.logger.debug("Accepting trade")
        # Check if trade window is open. Window can be closed if the player
        # cancelled the trade while we were calculating the state to be
        # accepted.
        if self.trade_window_tm.match_exists(
                self.lf.get(Locations.TRADE_WINDOW_FULL)):
            self.mc.click_at_location(
                self.lf.get(Locations.TRADE_ACCEPT_BUTTON))

    async def send_trade_request(self):
        self.logger.debug("Sending trade request to {}".format(self.trader))
        await asyncio.sleep(TradeStep.TRADE_REQUEST_SEND_DELAY)
        self.cc.player_console_command(self.trader, Commands.TRADE)

    async def offer(self):
        self.logger.debug("Offering item to trade")

        # Check if inventory is open. Inventory can be closed if the player
        # cancelled the trade.
        if not self.inventory_tm.match_exists(
                self.lf.get(Locations.INVENTORY_PANE)):
            return

        self.mc.move_mouse(self.lf.get(Locations.INVENTORY_0_0))
        self.kc.hold_modifier('Ctrl')
        self.mc.click()
        self.kc.unhold_modifier('Ctrl')
        self.mc.move_mouse(self.lf.get(Locations.SCREEN_NOOP_POSITION))

    async def on_accept(self):
        self.logger.debug("Trade accepted.")
        self.accepted = True
        self.cc.send_chat(self.trader, TradeStep.TRADE_THANK_YOU)
        self.state.update(States.ENDED)

    async def on_cancel(self):
        if self.retries <= 0:
            self.state.update(States.ENDED)
            return
        self.retries -= 1
        self.logger.debug("Trade cancelled. Retries left: {}".format(
            self.retries))
        await asyncio.sleep(TradeStep.RETRY_TIMEOUT)
        self.state.update(States.NOT_STARTED)

    async def on_left(self):
        self.logger.debug("Trader {} left the hideout.".format(self.trader))
        self.state.update(States.ENDED)

    def _kick_from_party(self):
        self.cc.player_console_command(self.trader, Commands.KICK_FROM_PARTY)

