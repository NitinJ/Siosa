import logging
import time

from siosa.client.log_listener import ClientLogListener
from siosa.control.game_state import GameState
from siosa.image.grid import Grid
from siosa.image.reusable_template_matcher import ReusableTemplateMatcher
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_state import States, TradeState


class TradeStateUpdater:
    OFFER_WAIT_TIME = 2
    ROWS = 5
    COLUMNS = 12
    BORDER = 3

    def __init__(self, game_state: GameState, trade_state: TradeState,
                 trade_info: TradeInfo, log_listener: ClientLogListener):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.log_listener = log_listener
        self.trade_status_queue = log_listener.trade_status_event_queue

        self.game_state = game_state

        self.trade_state = trade_state
        self.trade_info = trade_info
        self.trader = trade_info.trade_request.trader

        self.state_value = States.NOT_STARTED
        self.lf = LocationFactory()

        self.other_points = []
        self.ts_start = 0
        self.verifying = False

        self.awaiting_tm = TemplateMatcher(
            Template.from_registry(
                TemplateRegistry.AWAITING_TRADE_CANCEL_BUTTON),
            confirm_foreground=True)
        self.trading_tm_other = TemplateMatcher(
            Template.from_registry(TemplateRegistry.TRADE_WINDOW_OTHER_0_0),
            confirm_foreground=True)
        self.trading_tm_me = TemplateMatcher(
            Template.from_registry(TemplateRegistry.TRADE_WINDOW_ME_0_0),
            confirm_foreground=True)
        self.full_trading_tm = ReusableTemplateMatcher(
            Locations.TRADE_WINDOW_FULL, confirm_foreground=True)

        # Templates
        self.trade_window_title = Template.from_registry(
            TemplateRegistry.TRADE_WINDOW_TITLE)
        self.trade_accept_retracted = Template.from_registry(
            TemplateRegistry.TRADE_ACCEPT_RETRACTED)
        self.trade_green_aura = Template.from_registry(
            TemplateRegistry.TRADE_ACCEPT_GREEN_AURA)
        self.trade_cancel_accept_button = Template.from_registry(
            TemplateRegistry.CANCEL_TRADE_ACCEPT_BUTTON)
        self.trade_me_empty_text = Template.from_registry(
            TemplateRegistry.TRADE_WINDOW_ME_EMPTY_TEXT)

        self.grid_me = Grid(
            Locations.TRADE_WINDOW_ME,
            Locations.TRADE_WINDOW_ME_0_0,
            TradeStateUpdater.ROWS,
            TradeStateUpdater.COLUMNS,
            TradeStateUpdater.BORDER,
            TradeStateUpdater.BORDER)
        self.grid_other = Grid(
            Locations.TRADE_WINDOW_OTHER,
            Locations.TRADE_WINDOW_OTHER_0_0,
            TradeStateUpdater.ROWS,
            TradeStateUpdater.COLUMNS,
            TradeStateUpdater.BORDER,
            TradeStateUpdater.BORDER)

    def set_verifying(self, v):
        self.logger.debug("Setting verifying={}".format(v))
        self.verifying = v

    def update(self):
        ts = time.time()
        current_state = None
        trade_status = self._get_trade_status_from_log()
        game_state = self.game_state.get()
        self.full_trading_tm.clear_image_cache()

        if self.trader not in game_state['players_in_hideout']:
            current_state = States.LEFT
        elif trade_status:
            current_state = States.ACCEPTED if trade_status.accepted() else \
                States.CANCELLED
        elif self.awaiting_tm.match(self.lf.get(
                Locations.TRADE_AWAITING_TRADE_CANCEL_BUTTON)):
            current_state = States.AWAITING_TRADE
        elif self.full_trading_tm.match_template(self.trade_window_title):
            # Trading.
            self.logger.debug("Trade window is open")
            current_state = \
                States.create_from_trading_state(*self._get_trading_state())
            # This should never happen.
            assert current_state is not None
        else:
            current_state = States.NOT_STARTED

        if current_state != self.state_value:
            self.logger.debug(
                "Setting trade state to {}".format(current_state))
            self.state_value = current_state
            self.trade_state.set_value(self.state_value)

        self.logger.debug(
            "Update took: {} ms".format((time.time() - ts) * 1000))

    def _get_trading_state(self):
        ts = time.time()
        state_me = 'OFFERED' if self._have_i_offered() else 'NOT_OFFERED'
        state_other = 'NOT_OFFERED'
        if self.full_trading_tm.match_template(self.trade_accept_retracted):
            state_other = 'RETRACTED'
        elif self.full_trading_tm.match_template(self.trade_green_aura):
            state_other = 'ACCEPTED'
        else:
            state_other = 'OFFERED' if self._has_other_player_offered() else \
                'NOT_OFFERED'

        if self.full_trading_tm.match_template(self.trade_cancel_accept_button):
            state_me = 'ACCEPTED'
        self.logger.debug(
            "State me: {}, state_other: {}".format(state_me, state_other))
        return state_me, state_other

    def _have_i_offered(self):
        if self.full_trading_tm.match_template(self.trade_me_empty_text):
            return False
        empty_positions = \
            self.trading_tm_me.match(self.lf.get(Locations.TRADE_WINDOW_ME))
        return self.grid_me.get_cells_not_in_positions(empty_positions)

    def _has_other_player_offered(self):
        # Hack to make sure that we don't mark the other state as not-offered
        # when we are verifying items. While verifying, we need to hover over
        # items. Hover creates an overlay that hides cells in the other's trade
        # window. That leads to the code below to think that the other player
        # has retracted or changed the offering, thus marking the state as
        # NOT_OFFERED.
        if self.verifying:
            return True

        points = self.grid_other.get_cells_not_in_positions(
            self.trading_tm_other.match(
                self.lf.get(Locations.TRADE_WINDOW_OTHER)))
        self.logger.debug(
            "Other played has offered items at points {}".format(
                str(points)))
        t2 = time.time()
        if not points:
            return False
        elif not self.other_points or self.other_points != points:
            self.other_points = points
            self.ts_start = time.time()
            return False
        elif self.other_points == points and \
                t2 - self.ts_start >= TradeStateUpdater.OFFER_WAIT_TIME:
            return True
        return False

    def _get_trade_status_from_log(self):
        status = None
        while not self.trade_status_queue.empty():
            status = self.trade_status_queue.get()
        return status
