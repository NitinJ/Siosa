import os
import time

from siosa.common.util import parent
from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_state import GameState
from siosa.control.game_step import Step, StepStatus
from siosa.control.steps.utils import exit_edit_hideout_mode
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations


class PlaceStash(Step):
    DECORATIONS_LOAD_TIME = 5
    SEARCH_BOX_DELAY = 1

    """
    Places stash on the center of the screen. We cannot move to or get
    the stash co-ordinates so, we move the stash to the center of the
    screen.
    """

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.kc.keypress_with_modifiers(
            SiosaConfig().get_close_all_interfaces_shortcut())
        exit_edit_hideout_mode(self.lf, self.mc)

        tm = TemplateMatcher(TemplateRegistry.DECORATIONS_EDIT_BUTTON.get())
        if not tm.match_exists(self.lf.get(Locations.DECORATIONS_EDIT_BOX)):
            # Decoration edit box not open.
            self.mc.click_at_location(
                self.lf.get(Locations.DECORATIONS_EDIT_HIDEOUT_ARROW))

        self.mc.click_at_location(
            self.lf.get(Locations.DECORATIONS_OPEN_BUTTON))
        if not self.wait_for_decorations():
            return StepStatus(False)

        self.kc.keypress_with_modifiers(['ctrl', 'f'])
        time.sleep(PlaceStash.SEARCH_BOX_DELAY)

        self.kc.write('stash')
        self.mc.click_at_location(
            self.lf.get(Locations.DECORATIONS_STASH_AFTER_SEARCHING))
        self.mc.click_at_location(
            self.lf.get(Locations.DECORATIONS_CLOSE_BUTTON))
        self.mc.click_at_location(self.lf.get(Locations.SCREEN_CENTER))
        self.mc.click_at_location(
            self.lf.get(Locations.DECORATIONS_EDIT_HIDEOUT_BUTTON))
        self.mc.click_at_location(
            self.lf.get(Locations.DECORATIONS_EDIT_HIDEOUT_DOWN_ARROW))

        self.mc.click_at_location(self.lf.get(Locations.SCREEN_CENTER))
        game_state.update({
            'stash_location': self.lf.get(Locations.SCREEN_CENTER)
        })
        return StepStatus(True)

    def wait_for_decorations(self):
        # Sometimes the decorations take time to load.
        ts = time.time()
        tm = TemplateMatcher(TemplateRegistry.DECORATIONS_UTILITIES_ARROW.get())
        while not tm.match_exists(self.lf.get(Locations.DECORATIONS_PANE)):
            if time.time() - ts > PlaceStash.DECORATIONS_LOAD_TIME:
                return False
            time.sleep(0.1)

        return True


if __name__ == "__main__":
    config_file_path = os.path.join(parent(parent(parent(__file__))),
                                    "config.json")
    print(config_file_path)
    config = SiosaConfig.create_from_file(config_file_path)
    s = PlaceStash()

    s.execute(GameState())