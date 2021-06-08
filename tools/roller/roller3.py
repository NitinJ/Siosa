import logging
import time

from tools.roller.crafter import CrafterFactory
from tools.roller.crafting_type import get_crafting_type
from tools.roller.game_controller import GameController
from tools.roller.keyboard_shortcut import KeyboardShortcut
from tools.roller.kmcontroller import KMController
from tools.roller.roller_config import RollerConfig

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s \
    - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)


class Roller:
    LOG_FILE = "log.txt"
    COMBINATIONS = 'r+q'

    def __init__(self, roller_config, max_rolls=800):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.keyboard_listener = KeyboardShortcut(Roller.COMBINATIONS,
                                                  self.flip_rolling)
        self.roller_config = roller_config
        self.max_rolls = max_rolls
        self.currency_state = {}
        self.gc = GameController(debug=False)
        self.should_roll = True

    def flip_rolling(self):
        self.should_roll = not self.should_roll

    def start_rolling(self):
        self.keyboard_listener.start_listening()
        flog = open(Roller.LOG_FILE, "a+")
        for item in self.roller_config.get_items():
            crafting_type = get_crafting_type(item['crafting_type'])
            if crafting_type:
                self._roll_item(item, crafting_type, flog)

    def _roll_item(self, item, crafting_type, flog):
        self.gc.reset()
        self.gc.move_item_to_stash(item)

        crafter = CrafterFactory.get_crafter(item, crafting_type)
        for i in range(0, self.max_rolls):
            if not self.should_roll:
                raise Exception("Interrupted")

            in_game_item = self.gc.read_item()
            done, next_currency = crafter.done(in_game_item)

            self.log(flog, in_game_item, item, done, next_currency)
            if done:
                return self._on_success()
            if not done and not next_currency:
                return self._on_failure()

            try:
                self.gc.use_currency_on_item(next_currency)
            except:
                self.logger.info("Not enough currency: {}".format(
                    next_currency))
                return self._on_failure()

    def log(self, flog, in_game_item, item, matches, next_currency):
        log_str = "in_game_item: {}\nitem: {}\nmatches: {}\n" \
                  "next_currency:{}".format(in_game_item, item, matches,
                                            next_currency)
        if matches:
            self.logger.debug("Matched : {}".format(matches))
        flog.write(time.strftime("%a, %d %b %I:%M:%S %p:\n")
                   + log_str + "\n")

    def _on_success(self):
        self.logger.debug("Item rolled successfully !")
        self.gc.move_item_to_inventory()

    def _on_failure(self):
        self.logger.debug("Item rolling failed !")
        self.gc.move_item_to_inventory()


def run_timer():
    input("Press enter to confirm ...")
    t = 3
    for i in range(0, 3):
        time.sleep(1)
        print("Move to POE..({})".format(t - i))


if __name__ == "__main__":
    roller = Roller(RollerConfig('config.json'))
    run_timer()
    try:
        roller.start_rolling()
        print("All items successfully rolled !")
    except Exception as e:
        KMController().all_keys_up()
