import logging

import pyautogui

from tools.roller.clipboard import Clipboard
from tools.roller.currency import CurrencyStack
from tools.roller.item import Item
from tools.roller.kmcontroller import KMController
from tools.roller.locations import Locations


class GameController:
    INVENTORY_SLOT_SIZE = 53

    def __init__(self, debug=False):
        """
        Args:
            debug:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.debug = debug
        self.clipboard = Clipboard()
        self.picked_up_currency = None
        self.currency_info = {}
        self.km = KMController()

    def reset(self):
        self.km.all_keys_up()
        self.picked_up_currency = None

    def read_item(self):
        self.km.move_mouse(Locations.ITEM_LOCATION)
        self.km.copy_item_at_cursor()
        clipboard_data = self.clipboard.get_clipboard_data()
        item = Item.create_from_clipboard_data(clipboard_data)
        self.logger.debug("Item: {}".format(item))
        return item

    def read_currency(self, currency):
        """
        Args:
            currency:
        """
        currency_location = Locations.get_currency_location(currency)
        self.km.move_mouse(currency_location)
        self.km.copy_item_at_cursor()
        clipboard_data = self.clipboard.get_clipboard_data()
        currency_stack = CurrencyStack.create_from_clipboard_data(
            clipboard_data)
        self.currency_info[currency] = currency_stack.stack

    def pickup_currency(self, currency):
        """
        Args:
            currency:
        """
        self.logger.debug("Picking up currency: {}".format(currency))
        if currency == self.picked_up_currency:
            return
        if currency not in self.currency_info.keys():
            self.read_currency(currency)
        if self.currency_info[currency] <= 0:
            raise Exception("Out of currency !")
        self.km.move_mouse(Locations.get_currency_location(currency))
        self.km.click(button='right')
        self.picked_up_currency = currency

    def use_currency_on_item(self, currency):
        """
        Args:
            currency:
        """
        if currency != self.picked_up_currency:
            self.km.key_up('shift')
            self.pickup_currency(currency)
        if self.currency_info[currency] <= 0:
            raise Exception("Out of currency !")
        self.km.move_mouse(Locations.ITEM_LOCATION)
        self.km.key_down('shift')
        if not self.debug:
            # Only use currency when debug mode is off.
            self.km.click()
        self.currency_info[currency] -= 1

    def move_item_to_stash(self, item):
        """
        Args:
            item:
        """
        inventory_position = item['inventory_position']
        self.km.all_keys_up()
        r, c = inventory_position
        location = GameController.get_location_for_inventory_position(r, c)
        self.km.move_mouse(location)
        self.km.key_down('ctrl')
        pyautogui.click(button='left')
        self.km.key_up('ctrl')

    def move_item_to_inventory(self):
        self.km.all_keys_up()
        self.km.move_mouse(Locations.ITEM_LOCATION)
        self.km.key_down('ctrl')
        pyautogui.click(button='left')
        self.km.key_up('ctrl')

    @staticmethod
    def get_location_for_inventory_position(row, col):
        """
        Args:
            row:
            col:
        """
        location = Locations.INVENTORY_00
        x = location[0] + col * GameController.INVENTORY_SLOT_SIZE
        y = location[1] + row * GameController.INVENTORY_SLOT_SIZE
        return x, y, x, y
