import logging

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.mouse_controller import MouseController
from siosa.image.grid import Grid
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations, LocationFactory
from siosa.trader.currency_verifier import CurrencyVerifier


class TradeVerifier:
    ROWS = 5
    COLUMNS = 12
    BORDER = 2

    def __init__(self, trade_info):
        self.trade_info = trade_info
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.lf = LocationFactory()
        self.mc = MouseController(self.lf)
        self.clipboard = PoeClipboard()
        self.currency_verifier = CurrencyVerifier(trade_info.trade_request.currency)

        self.grid_other = Grid(
            Locations.TRADE_WINDOW_OTHER,
            Locations.TRADE_WINDOW_OTHER_0_0,
            TradeVerifier.ROWS,
            TradeVerifier.COLUMNS,
            TradeVerifier.BORDER,
            TradeVerifier.BORDER)
        self.trading_tm_other = TemplateMatcher(
            Template.from_registry(
                TemplateRegistry.TRADE_WINDOW_OTHER_SMALL_0_0),
            confirm_foreground=True)

    def verify(self):
        cells_with_items = self.grid_other.get_cells_not_in_positions(
            self.trading_tm_other.match(
                self.lf.get(Locations.TRADE_WINDOW_OTHER)))
        self.logger.debug("Items found at locations : {}".format(
            cells_with_items))
        items = []
        for cell in cells_with_items:
            cell_center = \
                self.grid_other.get_cell_location(cell).get_center_location()
            self.mc.move_mouse(cell_center)

            item = self.clipboard.read_item_at_cursor()
            if item:
                items.append(item)
            else:
                self.logger.debug(
                    "Could not parse item at cell location: {}".format(cell))

        self.logger.debug("Moving mouse to screen no-op position")
        self.mc.move_mouse(self.lf.get(Locations.SCREEN_NOOP_POSITION))

        return self.currency_verifier.verify(items)
