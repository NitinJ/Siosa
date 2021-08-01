import logging

from siosa.common.decorations import override
from siosa.control.game_task import Task
from siosa.control.keyboard_controller import KeyboardController
from siosa.control.mouse_controller import MouseController
from siosa.control.steps.pickup_inventory_item import PickupInventoryItem
from siosa.location.location_factory import LocationFactory, Locations
from siosa.roller.crafting_type import get_crafting_type
from siosa.roller.roll_controller import RollController
from siosa.roller.roll_step import RollStep
from siosa.roller.roller_config import RollerConfig


class RollTask(Task):
    DEFAULT_MAX_ROLLS = 1000

    def __init__(self, roller_config: RollerConfig):
        super().__init__(8, name='RollTask')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.roller_config = roller_config
        self.roller_config.validate_config()

        self.kc = KeyboardController()
        self.lf = LocationFactory()
        self.mc = MouseController(self.lf)
        self.roll_controller = RollController()

    @override
    def get_steps(self):
        for item in self.roller_config.get_items():
            crafting_type = get_crafting_type(item['crafting_type'])
            max_rolls = item['max_rolls'] if 'max_rolls' in item else \
                RollTask.DEFAULT_MAX_ROLLS
            yield PickupInventoryItem(tuple(item['inventory_position']))
            yield RollStep(
                self.roll_controller, item, crafting_type, max_rolls)
            self._transfer_item_back_to_inventory()

    def _transfer_item_back_to_inventory(self):
        self.kc.hold_modifier('ctrl')
        self.mc.click_at_location(self.lf.get(Locations.ITEM_LOCATION))
        self.kc.unhold_modifier('ctrl')

    @override
    def _cleanup_internal(self):
        self._transfer_item_back_to_inventory()
