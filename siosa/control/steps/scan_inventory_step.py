import logging
from enum import Enum

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.game_step import Step, StepStatus
from siosa.data.inventory import Inventory
from siosa.data.stash import Stash
from siosa.image.inventory_scanner import InventoryScanner
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations


class Error(Enum):
    STASH_TAB_NOT_FOUND = 0


def _update_items_with_width_height(items, item_cells):
    """
    Updates width and height of all items based on which cells they occupy
    in the inventory.
    Args:
        items: List of items
        item_cells: Map containing item: [cells] mapping
    Returns: None
    """
    for entry in items:
        key = str(entry['item'])
        if key not in item_cells.keys():
            continue
        cells = item_cells[key]
        min_i = min([cell[0] for cell in cells])
        max_i = max([cell[0] for cell in cells])
        min_j = min([cell[1] for cell in cells])
        max_j = max([cell[1] for cell in cells])
        entry['item'].set_dimensions(max_j - min_j + 1, max_i - min_i + 1)


class ScanInventory(Step):
    def __init__(self):
        Step.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.clipboard = PoeClipboard()
        self.inventory_scanner = InventoryScanner()
        self.inventory_0_0 = self.lf.get(Locations.INVENTORY_0_0)
        self.party_notification_tm = TemplateMatcher(Template.from_registry(
            TemplateRegistry.PARTY_NOTIFICATIONS_CLOSE_BUTTON))
        self.stash = Stash()
        self.items = []

    def execute(self, game_state):
        self.game_state = game_state

        self.close_all_party_notifications()
        item_positions = self.inventory_scanner.scan()
        item_cells = {}
        for p in item_positions:
            item = Inventory.get_item_at_cell(p)
            if not item:
                continue
            stash_tabs = self.stash.get_stash_tabs_for_item(item)

            if not stash_tabs:
                return StepStatus(False, Error.STASH_TAB_NOT_FOUND)

            stash_tab = stash_tabs[0]

            self.logger.info("Stash tab for item:{!s} is:{!s}".format(
                item, stash_tab))

            # De dupe items.
            key = str(item)
            if key not in item_cells.keys():
                # A item might get scanned multiple times if it's size is more
                # than 1x1. We only take one entry per item.
                item_cells[key] = []
                self.items.append({
                    'item': item,
                    'position': p,
                    'stash_tab': stash_tab,
                })
            item_cells[key].append(p)

        _update_items_with_width_height(self.items, item_cells)
        self.game_state.update({'inventory': self.items})
        self.logger.info(
            "Inventory items({}) scanned: {}".format(len(self.items),
                                                     self.items))
        return StepStatus(True)

    def get_party_notification_close_button_locations(self):
        party_notification_area = self.lf.get(
            Locations.PARTY_NOTIFICATIONS_AREA)
        points = self.party_notification_tm.match(party_notification_area)
        x, y = party_notification_area.x1, party_notification_area.y1
        # Create actual in game screen co-ordinates.
        return [self.lf.create(p[0] + x, p[1] + y, p[0] + x, p[1] + y)
                for p in points]

    def close_all_party_notifications(self):
        for pos in self.get_party_notification_close_button_locations():
            self.mc.click_at_location(pos)
