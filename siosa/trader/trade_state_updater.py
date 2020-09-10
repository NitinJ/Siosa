import logging

from siosa.control.game_state import GameState
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_state import States, TradeState


class TradeStateUpdater:
    def __init__(self, game_state: GameState, trade_state: TradeState,
                 trade_info: TradeInfo):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.game_state = game_state
        self.trade_state = trade_state
        self.trade_info = trade_info
        self.state_value = States.NOT_STARTED

        self.location_factory = LocationFactory()

        self.awaiting_tm = TemplateMatcher(
            Template.from_registry(
                TemplateRegistry.AWAITING_TRADE_CANCEL_BUTTON),
            confirm_if_poe_not_in_foreground=True)
        self.trading_tm = TemplateMatcher(
            Template.from_registry(TemplateRegistry.TRADE_WINDOW_TITLE),
            confirm_if_poe_not_in_foreground=True)

    def update(self):
        current_state = None
        if self.awaiting_tm.match(
                self.location_factory.get(Locations.AWAITING_TRADE_CANCEL_BUTTON)):
            current_state = States.AWAITING_TRADE
        elif self.trading_tm.match(
                self.location_factory.get(Locations.TRADE_WINDOW_TITLE)):
            current_state = self._get_trading_state()
        else:
            current_state = States.NOT_STARTED

        if current_state != self.state_value:
            self.logger.debug(
                "Setting trade state to {}".format(self.state_value))
            self.state_value = current_state
            self.trade_state.set_value(self.state_value)

    def _get_trading_state(self):
        return States.TRADING_NO_NO
