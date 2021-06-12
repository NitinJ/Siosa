import logging

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.mouse_controller import MouseController
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.poe_item import ItemType
from siosa.image.grid import Grid
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations, LocationFactory
from siosa.network.poe_api import PoeApi
from siosa.trader.currency_checker import CurrencyChecker
from siosa.trader.trade_request import TradeRequest
from siosa.trader.trade_window_currency_matcher import \
    TradeWindowCurrencyMatcher
from siosa.trader.verify_result import VerifyResult


class TradeVerifier:
    ROWS = 5
    COLUMNS = 12
    BORDER = 2
    SCALE = 1.5
    SUPPORTED_CURRENCY_TYPES = ['chaos', 'exalted']
    # In milliseconds
    MOUSE_MOVE_DURATION_FAST = 50 / 1000
    MOUSE_MOVE_DURATION_SLOW = 200 / 1000

    def __init__(self, trade_request):
        self.trade_request = trade_request
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.lf = LocationFactory()
        self.mc = MouseController()
        self.clipboard = PoeClipboard()
        self.currency_cheker = CurrencyChecker(trade_request.currency)

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
            confirm_foreground=True, debug=False)
        self.trade_window_currency_matcher = TradeWindowCurrencyMatcher(
            self.lf.get(Locations.TRADE_WINDOW_OTHER),
            confirm_foreground=True, debug=False, scale=TradeVerifier.SCALE)

    def _get_cells_with_items(self):
        cells_with_items = self.grid_other.get_cells_not_in_positions(
            self.trading_tm_other.match(
                self.lf.get(Locations.TRADE_WINDOW_OTHER)))
        cells_with_items = sorted(cells_with_items, key=lambda x: x[1])
        self.logger.debug("{} items found at locations : {}".format(
            len(cells_with_items), cells_with_items))
        return cells_with_items

    def _validate_item(self, item):
        if not item or item.type != ItemType.CURRENCY or not item.currency:
            return False
        return item.currency.trade_name in \
               CurrencyChecker.SUPPORTED_CURRENCY_TYPES

    def verify(self):
        cells = self._get_cells_with_items()
        items = []
        currency_stacks = {}

        for cell in cells:
            cell_center_location = \
                self.grid_other.get_cell_location(cell).get_center_location()
            self.mc.move_mouse(cell_center_location,
                               mouse_move_duration=TradeVerifier.MOUSE_MOVE_DURATION_FAST)
            item = self.clipboard.read_item_at_cursor()

            if not self._validate_item(item):
                self.logger.debug(
                    "Couldn't parse item at cell: {}".format(cell))
                return False

            items.append(item)
            key = (item.currency.trade_name, item.quantity)
            currency_stacks[key] = True

        self.logger.debug(
            "Got {} items from trade: {}".format(len(items), items))
        self.logger.debug("Currency stacks present: {}".format(currency_stacks))
        self.mc.move_mouse(self.lf.get(Locations.SCREEN_NOOP_POSITION))

        totals = self._get_currency_totals(items)
        res = VerifyResult(self.currency_cheker.get_diffs(totals), totals)
        self.logger.debug("Verify result from clipboard: {}".format(res))
        if not res.is_verified():
            return res

        # Re check if we still have the current currencies on the trade window
        # using template matching.
        totals2 = \
            self._get_currency_totals_using_tm(currency_stacks)
        res = VerifyResult(self.currency_cheker.get_diffs(totals2), totals2)
        self.logger.debug("Verify result from tm: {}".format(res))
        return res

    def _get_currency_totals(self, items):
        total = {
            'chaos': 0,
            'exalted': 0
        }
        for item in items:
            currency_type = item.currency.trade_name
            amount = item.quantity
            total[currency_type] = total[currency_type] + amount
        self.logger.debug("Got currency : {}".format(total))
        return total

    def _get_currency_totals_using_tm(self, currency_stacks):
        self.logger.info("Getting currency totals using tm.")
        total = {
            'chaos': 0,
            'exalted': 0
        }

        # We reset the matcher here so as to take screenshot again for multiple
        # calls to verifier. Otherwise it uses the old screenshot which can be
        # stale.
        self.trade_window_currency_matcher.clear_image_cache()

        for key in currency_stacks:
            currency_name = key[0]
            stack_size = key[1]
            template = Template.from_registry(
                TemplateRegistry.get_template_for_currency_stack(
                    currency_name, stack_size), scale=TradeVerifier.SCALE)
            matched_positions = \
                self.trade_window_currency_matcher.match_template(template)

            # Scale down positions.
            matched_positions = \
                [(m[0] // TradeVerifier.SCALE, m[1] // TradeVerifier.SCALE)
                 for m in matched_positions]
            cells = self.grid_other.get_cells_in_positions(matched_positions)
            n_matches = len(cells)
            total[currency_name] += n_matches * stack_size
            self.logger.debug(
                "{} cells found with currency stack: {}".format(n_matches, key))

        return total


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.ERROR)
    exchange = CurrencyExchange(
        PoeApi("MopedDriverr", "2561bcd7ed51683282115e110e6ea1f3"))
    trade_info = TradeRequest("Pew", "pew", {
        'type': 'chaos',
        'amount': 85.0
    }, 'pew', 'pew', (0, 0))
    print(TradeVerifier(trade_info).verify())
