import logging
import os
from enum import Enum

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.common.util import parent
from siosa.config.siosa_config import SiosaConfig
from siosa.control.console_controller import Commands
from siosa.control.game_state import GameState
from siosa.control.game_step import Step, StepStatus
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.inventory import Inventory
from siosa.data.stash import Stash
from siosa.image.inventory_scanner import InventoryScanner
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations, LocationFactory
from siosa.network.poe_api import PoeApi


class Error(Enum):
    STASH_TAB_NOT_FOUND = 0
    INVENTORY_NOT_OPEN = 1


class ScanInventory(Step):
    def __init__(self):
        Step.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.clipboard = PoeClipboard()
        self.inventory_scanner = InventoryScanner()
        self.inventory_0_0 = self.lf.get(Locations.INVENTORY_0_0)
        self.party_notification_tm = TemplateMatcher(
            TemplateRegistry.PARTY_NOTIFICATIONS_CLOSE_BUTTON.get())
        self.inventory_banner_tm = TemplateMatcher(
            TemplateRegistry.INVENTORY_BANNER.get())
        self.stash = Stash()
        self.items = []

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state
        if not self._is_inventory_open():
            return StepStatus(False, Error.INVENTORY_NOT_OPEN)

        self.clear_chat_messages()
        self.close_all_party_notifications()

        # Cells which are occupied by items.
        item_cells = {}

        for p in self.inventory_scanner.scan():
            if p in item_cells:
                # The current position is part of an already scanned item, so
                # skip it.
                continue

            item = Inventory.get_item_at_cell(p)
            if not item:
                continue
            stash_tabs = self.stash.get_stash_tabs_for_item(item)

            if not stash_tabs:
                return StepStatus(False, Error.STASH_TAB_NOT_FOUND)

            stash_tab = stash_tabs[0]
            self.logger.info("Stash tab for item:{!s} is:{!s}".format(
                item, stash_tab))

            # Mark the cells which this item occupies.
            ScanInventory._mark_item_cells(p, item, item_cells)
            self.items.append({
                'item': item,
                'position': p,
                'stash_tab': stash_tab,
            })

        self.game_state.update({'inventory': self.items})
        self.logger.info(
            "Inventory items({}) scanned: {}".format(len(self.items),
                                                     self.items))
        return StepStatus(True)

    @staticmethod
    def _mark_item_cells(p, item, cells):
        """
        Args:
            p:
            item:
            cells:
        """
        w, h = item.get_dimensions()
        if not w or not h:
            w = 1
            h = 1
        p2 = (p[0] + h - 1, p[1] + w - 1)
        for i in range(p[0], p2[0] + 1):
            for j in range(p[1], p2[1] + 1):
                cells[(i, j)] = True

    def get_party_notification_close_button_locations(self):
        party_notification_area = self.lf.get(
            Locations.PARTY_NOTIFICATIONS_AREA)
        points = self.party_notification_tm.match(party_notification_area)
        x, y = party_notification_area.x1, party_notification_area.y1
        # Create actual in game screen co-ordinates.
        return [self.lf.create(p[0] + x, p[1] + y, p[0] + x, p[1] + y)
                for p in points]

    def clear_chat_messages(self):
        self.cc.console_command(Commands.CLEAR)

    def close_all_party_notifications(self):
        for pos in self.get_party_notification_close_button_locations():
            self.mc.click_at_location(pos)

    def _is_inventory_open(self):
        return len(self.inventory_banner_tm.match(self.lf.get(
            Locations.INVENTORY_BANNER))) > 0

if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.ERROR)

    lf = LocationFactory()
    exchange = CurrencyExchange(
        PoeApi("MopedDriverr", "0dfdc62a6d647095161d19e802961ef3",
               "Expedition"))
    config_file_path = os.path.join(parent(parent(parent(__file__))), "config.json")
    print(config_file_path)
    config = SiosaConfig.create_from_file(config_file_path)
    stash = Stash(config)

    gs = GameState()
    print(ScanInventory().execute(gs))