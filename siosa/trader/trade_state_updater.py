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
        self._get_trade_status_from_log()

        self.game_state = game_state

        self.trade_state = trade_state
        self.trade_info = trade_info
        self.trader = trade_info.trade_request.trader

        self.current_state = States.NOT_STARTED
        self.lf = LocationFactory()

        self.other_points = []
        self.ts_start = 0

        self.awaiting_tm = TemplateMatcher(
            Template.from_registry(
                TemplateRegistry.AWAITING_TRADE_CANCEL_BUTTON),
            confirm_foreground=True, scale=0.5)
        self.trading_tm_other = TemplateMatcher(
            Template.from_registry(TemplateRegistry.TRADE_WINDOW_OTHER_SMALL_0_0),
            confirm_foreground=True, scale=0.5)
        self.trading_tm_me = TemplateMatcher(
            Template.from_registry(TemplateRegistry.TRADE_WINDOW_ME_0_0),
            confirm_foreground=True, scale=0.5)
        self.full_trading_tm = ReusableTemplateMatcher(
            Locations.TRADE_WINDOW_FULL, confirm_foreground=True, scale=0.5)

        # Templates
        self.trade_window_close_button = Template.from_registry(
            TemplateRegistry.TRADE_WINDOW_CLOSE_BUTTON, scale=0.5)
        self.trade_accept_retracted = Template.from_registry(
            TemplateRegistry.TRADE_ACCEPT_RETRACTED, scale=0.5)
        self.trade_green_aura = Template.from_registry(
            TemplateRegistry.TRADE_ACCEPT_GREEN_AURA, scale=0.5)
        self.trade_cancel_accept_button = Template.from_registry(
            TemplateRegistry.CANCEL_TRADE_ACCEPT_BUTTON, scale=0.5)
        self.trade_me_empty_text = Template.from_registry(
            TemplateRegistry.TRADE_WINDOW_ME_EMPTY_TEXT, scale=0.5)

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

    def update(self):
        self.current_state = self.trade_state.get()
        self.logger.debug("In update ----------------------State: {}".format(
            self.current_state))
        ts = time.time()

        trade_status = self._get_trade_status_from_log()
        game_state = self.game_state.get()
        self.full_trading_tm.clear_image_cache()

        new_state = None
        if self.full_trading_tm.match_template(self.trade_window_close_button):
            self.logger.debug("Trade window is open.")
            new_state = self._get_trading_state()
        elif self.trader not in game_state['players_in_hideout']:
            new_state = States.LEFT
        elif trade_status:
            new_state = States.ACCEPTED if trade_status.accepted() else \
                States.CANCELLED
        elif self.awaiting_tm.match(self.lf.get(
                Locations.TRADE_AWAITING_TRADE_CANCEL_BUTTON)):
            new_state = States.AWAITING_TRADE

        state_changed = False
        if new_state and new_state != self.current_state:
            if str(self.current_state) == self.trade_state.get():
                self.logger.debug("Trying to set state to {}".format(new_state))
                self.current_state = new_state
                state_changed = self.trade_state.update(new_state)
            else:
                self.logger.debug("Internal state changed but trade_state has "
                                  "already changed. Discarding current run of "
                                  "the updater")

        if state_changed:
            self.logger.debug("State changed to {}".format(new_state))

        self.logger.debug(
            "Update took: {} ms".format((time.time() - ts) * 1000))

    def _get_trading_state(self):
        ts = time.time()

        # My state.
        if self.full_trading_tm.match_template(self.trade_cancel_accept_button):
            state_me = 'ACCEPTED'
        else:
            state_me = 'OFFERED' if self._have_i_offered() else 'NOT_OFFERED'

        # Other state.
        state_other = 'NOT_OFFERED'
        if self.full_trading_tm.match_template(self.trade_accept_retracted):
            state_other = 'RETRACTED'
        elif self.full_trading_tm.match_template(self.trade_green_aura):
            state_other = 'ACCEPTED'
        else:
            state_other = 'OFFERED' if self._has_other_player_offered() else \
                'NOT_OFFERED'

        self.logger.debug(
            "State me: {}, state_other: {}".format(state_me, state_other))

        return States.create_from_trading_state(state_me, state_other)

    def _have_i_offered(self):
        return not self.full_trading_tm.match_template(self.trade_me_empty_text)

    def _has_other_player_offered(self):
        points = self.grid_other.get_cells_not_in_positions(
            self.trading_tm_other.match(
                self.lf.get(Locations.TRADE_WINDOW_OTHER)))
        if points:
            self.logger.debug(
                "Other played has offered items at points {}".format(
                    str(points)))
            return True
        return False

    def _get_trade_status_from_log(self):
        status = None
        while not self.trade_status_queue.empty():
            status = self.trade_status_queue.get()
        return status
