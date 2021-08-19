import time
from enum import Enum

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.game_step import Step, StepStatus
from siosa.data.poe_currencies import CurrencyStack
from siosa.data.stash import Stash
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations


class Error(Enum):
    STASH_NOT_OPEN = 0
    ITEM_NOT_FOUND_IN_STASH_TAB = 1
    STASH_TAB_NOT_OPEN = 2
    COULD_NOT_READ_ITEM = 3
    COULD_NOT_OPEN_PRICE_WINDOW = 4
    STASH_TAB_NOT_PRICIBLE = 5


class PriceItem(Step):
    PRICE_STR = "~price {} {}"

    def __init__(self, stash_index, stash_cell, currency_stack=None):
        """
        Args:
            stash_index:
            stash_cell:
            currency_stack:
        """
        Step.__init__(self)
        self.stash_index = stash_index
        self.stash_cell = stash_cell

        self.stash_tab = Stash().get_stash_tab_by_index(stash_index)
        assert self.stash_tab is not None

        self.price_note = PriceItem._get_price_note(currency_stack)
        self.poe_clipboard = PoeClipboard()
        self.tm_arrow = \
            TemplateMatcher(TemplateRegistry.PRICE_ITEM_WINDOW_ARROW.get())

    @staticmethod
    def _get_price_note(currency_stack):
        """
        Args:
            currency_stack:
        """
        return PriceItem.PRICE_STR.format(currency_stack.quantity,
                                          currency_stack.currency.trade_name)

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state.get()
        if not self.game_state['stash_open']:
            return StepStatus(False, Error.STASH_NOT_OPEN)
        if self.game_state['open_stash_tab_index'] != self.stash_index:
            return StepStatus(False, Error.STASH_TAB_NOT_OPEN)

        # Check if item is present in cell and not present in stash cell.
        if not self.stash_tab.is_item_at_location_ingame(self.stash_cell):
            return StepStatus(False, Error.ITEM_NOT_FOUND_IN_STASH_TAB)
        self.mc.move_mouse(self.stash_tab.get_cell_location(self.stash_cell))

        # Read item at cursor.
        item = self.poe_clipboard.read_item_at_cursor()
        if not item:
            return StepStatus(False, Error.COULD_NOT_READ_ITEM)

        # Open pricing window.
        self.mc.right_click()

        # Check if pricing window opens.
        points = self.tm_arrow.match(self.lf.get(Locations.SCREEN_FULL))
        if not points:
            # Pricing window doesn't open.
            return StepStatus(False, Error.STASH_TAB_NOT_PRICIBLE)

        # Check if item is already priced.
        if "~price" in item.item_info['note']:
            # Already priced.
            self.logger.info("Item is already priced.")
            if not self._focus_note_option():
                return StepStatus(False, Error.COULD_NOT_OPEN_PRICE_WINDOW)

        # Set price.
        time.sleep(0.5)
        self.kc.write(self.price_note)
        self.kc.keypress('enter')
        return StepStatus(True)

    def _focus_note_option(self):
        """Focuses the note option textbox assuming that the pricing window is
        already open. Returns: Whether the note option textbox could be
        focussed.
        """
        points = self.tm_arrow.match(self.lf.get(Locations.SCREEN_FULL))
        if not points:
            # Arrow not found somehow.
            return False

        point = points[0]
        self.mc.click_at_location(
            self.lf.create(point[0], point[1], point[0], point[1]))

        # Move to note and select it.
        self.kc.keypress('up')
        self.kc.keypress('up')
        self.kc.keypress('up')
        self.kc.keypress('up')

        # Open up the edit box for note.
        self.kc.keypress('enter')

        # Move focus to note.
        self.kc.keypress('tab')
        return True
