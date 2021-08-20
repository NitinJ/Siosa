import logging
import time

from siosa.client.log_listener import ClientLogListener
from siosa.control.game_state import GameState
from siosa.image.grid import Grid
from siosa.image.reusable_template_matcher import ReusableTemplateMatcher
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_state import States, TradeState


class TradeStateUpdater:
    ROWS = 5
    COLUMNS = 12
    BORDER = 3

    def __init__(self, game_state: GameState, trade_state: TradeState,
                 trade_info: TradeInfo, log_listener: ClientLogListener):
        """
        Args:
            game_state (GameState):
            trade_state (TradeState):
            trade_info (TradeInfo):
            log_listener (ClientLogListener):
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.lf = LocationFactory()
        self.game_state = game_state

        # Actual state of trade. This can be updated from outside of this class.
        self.trade_state = trade_state
        self.trader = trade_info.trade_request.trader

        self.log_listener = log_listener
        self.trade_status_queue = log_listener.trade_status_event_queue
        self._get_trade_status_from_log()

        # Matchers
        self.awaiting_tm = TemplateMatcher(
            TemplateRegistry.AWAITING_TRADE_CANCEL_BUTTON.get())
        self.trading_tm_other = TemplateMatcher(
            TemplateRegistry.TRADE_WINDOW_OTHER_SMALL_0_0.get())
        self.trade_green_aura_tm = TemplateMatcher(
            TemplateRegistry.TRADE_ACCEPT_GREEN_AURA.get())

        # Reusable matchers
        self.full_trading_tm = ReusableTemplateMatcher(
            self.lf.get(Locations.TRADE_WINDOW_FULL))

        # Templates
        self.trade_window_close_button = \
            TemplateRegistry.TRADE_WINDOW_CLOSE_BUTTON.get()
        self.trade_accept_retracted = \
            TemplateRegistry.TRADE_ACCEPT_RETRACTED.get()
        self.trade_cancel_accept_button = \
            TemplateRegistry.CANCEL_TRADE_ACCEPT_BUTTON.get()
        self.trade_me_empty_text = \
            TemplateRegistry.TRADE_WINDOW_ME_EMPTY_TEXT.get()

        self.grid_other = Grid(
            Locations.TRADE_WINDOW_OTHER,
            Locations.TRADE_WINDOW_OTHER_0_0,
            TradeStateUpdater.ROWS,
            TradeStateUpdater.COLUMNS,
            TradeStateUpdater.BORDER,
            TradeStateUpdater.BORDER)

    def update(self):
        trade_state_at_start = self.trade_state.to_string()
        self.logger.debug("In update with state:{} --------------------".format(
            trade_state_at_start))
        ts = time.time()

        state = self._get_state()
        self.logger.debug("Updater calculated state: {}".format(state))

        if state and state != trade_state_at_start:
            # State changed
            if trade_state_at_start != self.trade_state.to_string():
                self.logger.debug("Internal state changed but trade_state has "
                                  "already changed. Discarding current run of "
                                  "the updater.")
            elif self.trade_state.update(state):
                self.logger.debug("State changed to {}".format(state))
        self.logger.debug(
            "Update took: {} ms".format((time.time() - ts) * 1000))

    def _get_state(self) -> States:
        """Calculates the current state of trade by using template matching,
        based on a number of factors like- trade window, player presence in
        hideout etc. Returns: The calculated state
        """
        game_state = self.game_state.get()
        trade_status = self._get_trade_status_from_log()
        self.full_trading_tm.clear_image_cache()
        if self.full_trading_tm.match_exists(self.trade_window_close_button):
            self.logger.debug("Trade window is open.")
            return self._get_trading_state()

        if self.trader not in game_state['players_in_hideout']:
            return States.LEFT

        if trade_status:
            return States.ACCEPTED if trade_status.accepted() else \
                States.CANCELLED

        if self.awaiting_tm.match_exists(self.lf.get(
                Locations.TRADE_AWAITING_TRADE_CANCEL_BUTTON)):
            return States.AWAITING_TRADE

    def _get_trading_state(self) -> States:
        # My state.
        if self.full_trading_tm.match_exists(self.trade_cancel_accept_button):
            state_me = 'ACCEPTED'
        else:
            state_me = 'OFFERED' if self._have_i_offered() else 'NOT_OFFERED'

        # Other state.
        state_other = 'NOT_OFFERED'
        if self.full_trading_tm.match_exists(self.trade_accept_retracted):
            state_other = 'RETRACTED'
        elif self.trade_green_aura_tm.match_exists(
                self.lf.get(Locations.TRADE_ACCEPT_GREEN_AURA_BOX)):
            state_other = 'ACCEPTED'
        else:
            state_other = 'OFFERED' if self._has_other_player_offered() else \
                'NOT_OFFERED'

        self.logger.debug(
            "State me: {}, state_other: {}".format(state_me, state_other))

        return States.create_from_trading_state(state_me, state_other)

    def _have_i_offered(self) -> bool:
        return not self.full_trading_tm.match_exists(self.trade_me_empty_text)

    def _has_other_player_offered(self) -> bool:
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
