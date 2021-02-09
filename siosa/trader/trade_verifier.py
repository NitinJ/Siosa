import logging

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.mouse_controller import MouseController
from siosa.data.poe_item import ItemType
from siosa.image.grid import Grid
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations, LocationFactory



class TradeVerifier:
    ROWS = 5
    COLUMNS = 12
    BORDER = 2
    SUPPORTED_CURRENCY_TYPES = ['chaos', 'exalted']

    def __init__(self, trade_info):
        self.trade_info = trade_info
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.lf = LocationFactory()
        self.mc = MouseController(self.lf)
        self.clipboard = PoeClipboard()

        self.grid_other = Grid(
            Locations.TRADE_WINDOW_OTHER,
            Locations.TRADE_WINDOW_OTHER_0_0,
            TradeVerifier.ROWS,
            TradeVerifier.COLUMNS,
            TradeVerifier.BORDER,
            TradeVerifier.BORDER)
        self.trading_tm_other = TemplateMatcher(
            Template.from_registry(TemplateRegistry.TRADE_WINDOW_OTHER_SMALL_0_0),
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
                self.logger.debug("Could not parse item at cell location: {}".format(cell))

        self.logger.debug("Moving mouse to screen no-op position")
        self.mc.move_mouse(self.lf.get(Locations.SCREEN_NOOP_POSITION))

        return self._verify_currency(items)

    def _verify_currency(self, scanned_items):
        currency_type_required = self.trade_info.trade_request.currency['type']
        currency_amount_required = self.trade_info.trade_request.currency['amount']
        currency_amount_got = 0
        for item in scanned_items:
            if item.type and item.type != ItemType.CURRENCY:
                return False
            if item.currency.trade_name not in TradeVerifier.SUPPORTED_CURRENCY_TYPES:
                return False
            if item.currency.trade_name != currency_type_required:
                return False
            self.logger.debug("Got currency {}: {}".format(item.currency.trade_name, item.quantity))
            currency_amount_got = currency_amount_got + item.quantity
        return currency_amount_required == currency_amount_got
