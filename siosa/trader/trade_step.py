import asyncio
import time

from siosa.control.console_controller import Commands
from siosa.control.game_step import Step
from siosa.dfa.dfa import Dfa
from siosa.location.location_factory import LocationFactory, Locations
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_state import States, TradeState
from siosa.trader.trade_state_updater import TradeStateUpdater
from siosa.trader.trade_verifier import TradeVerifier


class TradeStep(Step):
    UPDATE_INTERVAL = 0.005
    MAX_RETRIES = 2
    TRADE_THANK_YOU = "Thanks and have fun !"
    TRADE_OFFER_WAIT_TIMEOUT = 20
    TRADE_ACCEPT_WAIT_TIMEOUT = 10

    def __init__(self, trade_info: TradeInfo, log_listener):
        super().__init__()
        self.trade_info = trade_info
        self.trader = self.trade_info.trade_request.trader
        self.lf = LocationFactory()
        self.state_updater = None
        self.log_listener = log_listener

        # Current trade state.
        self.state = TradeState(States.NOT_STARTED)
        self.updater_end_states = [
            TradeState(States.ACCEPTED),
            TradeState(States.LEFT),
            TradeState(States.ENDED)
        ]
        self.dfa = Dfa(self.state, TradeState(States.ENDED))

        # Trade state variables.
        self.retries = 0
        self.accepted = False

        self.trade_verifier = TradeVerifier(trade_info)

        self._initialize_state_transitions()

    def execute(self, game_state):
        self.game_state = game_state
        self.state_updater = TradeStateUpdater(
            game_state, self.state, self.trade_info, self.log_listener)

        self.dfa.start()
        while not self._updater_end_state_reached():
            self.state_updater.update()
            time.sleep(TradeStep.UPDATE_INTERVAL)
        self.dfa.join()

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
        self.dfa.add_state_fn(TradeState(States.TRADING_NO_R), self.offer)
        self.dfa.add_state_fn(TradeState(States.TRADING_NO_A), self.offer)

        # Offered
        self.dfa.add_state_fn(TradeState(States.TRADING_O_NO),
                              self.cancel(offer_timeout))
        self.dfa.add_state_fn(TradeState(States.TRADING_O_O), self.verify)
        self.dfa.add_state_fn(TradeState(States.TRADING_O_A), self.verify)

        # Verified success
        self.dfa.add_state_fn(TradeState(States.TRADING_VS_NO),
                              self.transition(States.TRADING_O_NO))
        self.dfa.add_state_fn(TradeState(States.TRADING_VS_O), self.accept)
        self.dfa.add_state_fn(TradeState(States.TRADING_VS_A), self.accept)

        # Verified fail
        self.dfa.add_state_fn(TradeState(States.TRADING_VF_NO),
                              self.transition(States.TRADING_O_NO))
        self.dfa.add_state_fn(TradeState(States.TRADING_VF_O),
                              self.cancel(offer_timeout))
        self.dfa.add_state_fn(TradeState(States.TRADING_VF_A),
                              self.cancel(0))

        # Accepted
        self.dfa.add_state_fn(TradeState(States.TRADING_A_NO),
                              self.transition(States.TRADING_O_NO))
        self.dfa.add_state_fn(TradeState(States.TRADING_A_O),
                              self.cancel(accept_timeout))

        # End
        self.dfa.add_state_fn(TradeState(States.ENDED), self.on_end)

    def transition(self, state_value):
        async def wrapper():
            self.state.set_value(state_value)
        return wrapper

    def cancel(self, timeout):
        async def wrapper():
            await asyncio.sleep(timeout)
            self.state.set_value(States.CANCELLED)
        return wrapper

    async def verify(self):
        self.logger.debug("Verifying trade".format(self.trader))
        if self.trade_verifier.verify():
            self.state.set_state_me_str('VERIFIED_SUCCESS')
        else:
            self.state.set_state_me_str('VERIFIED_FAIL')

    async def accept(self):
        self.logger.debug("Accepting trade")
        self.mc.click_at_location(self.lf.get(Locations.TRADE_ACCEPT_BUTTON))

    async def send_trade_request(self):
        self.logger.debug("Sending trade request to {}".format(self.trader))
        self.cc.console_command(Commands.TRADE(self.trader))

    async def offer(self):
        self.logger.debug("Offering item to trade")
        self.mc.move_mouse(self.lf.get(Locations.INVENTORY_0_0))
        self.kc.hold_modifier('Ctrl')
        self.mc.click()
        self.kc.unhold_modifier('Ctrl')
        self.mc.move_mouse(self.lf.get(Locations.OPEN_POSITION))

    async def on_accept(self):
        self.logger.debug("Trade accepted.")
        self.accepted = True
        self.cc.send_chat(self.trader, TradeStep.TRADE_THANK_YOU)
        self.state.set_value(States.ENDED)

    async def on_cancel(self):
        self.logger.debug("Trade cancelled. Reties left: {}".format(
            TradeStep.MAX_RETRIES - self.retries))
        if self.retries >= TradeStep.MAX_RETRIES:
            self.state.set_value(States.ENDED)
            return
        self.retries += 1
        self.state.set_value(States.NOT_STARTED)

    async def on_left(self):
        self.logger.debug("Trader {} left the hideout.".format(self.trader))
        self.state.set_value(States.ENDED)

    def _updater_end_state_reached(self):
        for end_state in self.updater_end_states:
            if self.state.equals(end_state):
                return True
        return False

    def on_end(self):
        self.logger.debug("Trade ended.")
        self._kick_from_party()
        if not self.accepted:
            self._cleanup()
        self.logger.debug("Trade ended. Done.")

    def _cleanup(self):
        # Move item back to where it was and price it the same.
        pass

    def _kick_from_party(self):
        self.cc.console_command(Commands.KICK_FROM_PARTY(self.trader))
