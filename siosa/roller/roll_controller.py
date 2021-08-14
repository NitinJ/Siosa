import logging
import time

import pyautogui

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.keyboard_controller import KeyboardController
from siosa.control.mouse_controller import MouseController
from siosa.data.inventory import Inventory
from siosa.location.location_factory import LocationFactory, Locations
from siosa.roller.utils import get_item_location, get_currency_location


class RollController:
    INVENTORY_SLOT_SIZE = 53
    SAME_CURRENCY_ROLL_DELAY = 0.25
    READ_DELAY = 0.0

    def __init__(self, debug=False):
        """
        Args:
            debug:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.debug = debug

        self.clipboard = PoeClipboard()
        self.kc = KeyboardController()
        self.mc = MouseController(LocationFactory())
        self.lf = LocationFactory()

        self.picked_up_currency_type = None
        self.last_read = time.time()
        self.currency_info = {}

    def reset(self):
        self.kc.unhold()
        self.picked_up_currency_type = None

    def read_item(self):
        ts = time.time()
        if ts - self.last_read < RollController.READ_DELAY:
            time.sleep(RollController.READ_DELAY - ts + self.last_read)
        self.mc.move_mouse(get_item_location())
        item = self.clipboard.read_item_at_cursor()
        self.last_read = time.time()
        self.logger.debug("Item: {}".format(item))
        return item

    def read_currency(self, currency_type):
        """
        Args:
            currency_type:
        """
        self.mc.move_mouse(get_currency_location(currency_type))
        currency_stack = self.clipboard.read_item_at_cursor()
        self.currency_info[currency_type] = currency_stack.quantity

    def pickup_currency(self, currency_type):
        """
        Args:
            currency_type:
        """
        self.logger.debug(
            "Picking up currency_type: {}".format(currency_type))
        if currency_type == self.picked_up_currency_type:
            return

        if currency_type not in self.currency_info.keys():
            self.read_currency(currency_type)

        if self.currency_info[currency_type] <= 0:
            raise Exception("Out of currency: {}".format(currency_type))

        self.mc.move_mouse(get_currency_location(currency_type))
        self.mc.right_click()
        self.picked_up_currency_type = currency_type

    def use_currency_on_item(self, currency_type):
        """
        Args:
            currency_type:
        """
        self.logger.debug("Use currency on item: {}".format(currency_type))
        if currency_type != self.picked_up_currency_type:
            self.kc.unhold_modifier('shift')
            self.pickup_currency(currency_type)
        else:
            time.sleep(RollController.SAME_CURRENCY_ROLL_DELAY)

        if self.currency_info[currency_type] <= 0:
            raise Exception("Out of currency: {}".format(currency_type))

        self.mc.move_mouse(get_item_location())
        self.kc.hold_modifier('shift')

        if not self.debug:
            # Only use currency_type when debug mode is off.
            self.mc.click()

        self.currency_info[currency_type] -= 1

    def move_item_to_stash(self, item):
        """
        Args:
            item:
        """
        self.kc.unhold()
        location = Inventory.get_location(item['inventory_position'])
        self.mc.move_mouse(location)
        self.kc.hold_modifier('ctrl')
        pyautogui.click(button='left')
        self.kc.unhold_modifier('ctrl')

    def move_item_to_inventory(self):
        self.kc.unhold()
        self.mc.move_mouse(get_item_location())
        self.kc.hold_modifier('ctrl')
        pyautogui.click(button='left')
        self.kc.unhold_modifier('ctrl')
