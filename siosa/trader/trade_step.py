import time

from siosa.control.console_controller import Commands
from siosa.control.game_step import Step
from siosa.dfa.dfa import Dfa
from siosa.location.location_factory import LocationFactory, Locations
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_state import States, TradeState
from siosa.trader.trade_state_updater import TradeStateUpdater


class TradeStep(Step):
    SLEEP_DURATION = 0.01
    MAX_RETRIES = 3

    def __init__(self, trade_info: TradeInfo):
        super().__init__()
        self.trade_info = trade_info
        self.lf = LocationFactory()
        self.state_updater = None
        self.state = TradeState(States.NOT_STARTED)
        self.end = TradeState(States.ACCEPTED)
        self.dfa = Dfa(self.state, self.end)
        self.retries = 0
        self._initialize_state_transitions()

    def execute(self, game_state):
        self.game_state = game_state
        self.state_updater = TradeStateUpdater(game_state, self.state, self.trade_info)
        self.dfa.start()
        while not self.state.equals(self.end):
            self.state_updater.update()
            time.sleep(TradeStep.SLEEP_DURATION)

    def _update_trade_state(self):
        pass

    def _initialize_state_transitions(self):
        self.dfa.add_state_fn(TradeState(States.NOT_STARTED), self.send_trade_request)
        self.dfa.add_state_fn(TradeState(States.TRADING_NO_NO), self.offer)

    async def send_trade_request(self):
        if self.retries >= TradeStep.MAX_RETRIES:
            self.state.set_value(States.CANCELLED)
            return
        self.retries += 1
        trader = self.trade_info.trade_request.trader
        self.logger.debug("Sending trade request to {}".format(trader))
        self.cc.console_command(Commands.TRADE(trader))

    async def offer(self):
        self.logger.debug("Offering item to trade")
        self.kc.hold_modifier('Ctrl')
        self.mc.click_at_location(self.lf.get(Locations.INVENTORY_0_0))
        self.kc.unhold_modifier('Ctrl')
        self.mc.move_mouse(self.lf.get(Locations.OPEN_POSITION))