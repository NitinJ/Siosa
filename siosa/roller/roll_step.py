import time
from enum import Enum

from siosa.control.game_step import Step, StepStatus
from siosa.roller.crafter import CrafterFactory
from siosa.roller.crafting_type import CraftingType
from siosa.roller.roll_controller import RollController


class Error(Enum):
    UNKNOWN = 0
    ITEM_NOT_FOUND = 1
    OUT_OF_CURRENCY = 2


class RollStep(Step):
    """
    Rolls a single item placed in currency stash's item window based on
    crafting type.
    """

    def __init__(self, roll_controller: RollController, item,
                 crafting_type: CraftingType, max_rolls):
        Step.__init__(self)
        self.roll_controller = roll_controller
        self.item = item
        self.crafting_type = crafting_type
        self.max_rolls = max_rolls

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.roll_controller.reset()
        crafter = CrafterFactory.get_crafter(self.item, self.crafting_type)
        n_retries = 10

        for _ in range(self.max_rolls):
            time.sleep(0.1)
            in_game_item = self.roll_controller.read_item()
            if not in_game_item:
                if n_retries > 0:
                    time.sleep(0.1)
                    n_retries -= 1
                    continue
                return self._on_failure(Error.ITEM_NOT_FOUND)

            done, next_currency = crafter.done(in_game_item)
            self.logger.debug(
                "in_game_item: {}, item: {}\ndone: {}, next_currency:{}"
                    .format(in_game_item, self.item, done, next_currency))

            if done:
                return self._on_success()
            if not done and not next_currency:
                return self._on_failure(Error.UNKNOWN)

            try:
                self.logger.debug("Using currency")
                self.roll_controller.use_currency_on_item(next_currency)
            except:
                self.logger.error(
                    "Error using currency ({}) on item".format(
                        next_currency), stack_info=True, exc_info=True)
                return self._on_failure(Error.OUT_OF_CURRENCY)

    def _on_success(self):
        self.logger.debug("Item rolled successfully !")
        self.roll_controller.reset()
        return StepStatus(True)

    def _on_failure(self, error):
        self.logger.debug("Item rolling failed !")
        self.roll_controller.reset()
        return StepStatus(False, error)

