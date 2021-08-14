import time

from siosa.control.game_step import Step, StepStatus
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations


class PlaceStash(Step):
    DECORATIONS_LOAD_TIME = 1.5
    SEARCH_BOX_DELAY = 0.3

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
        stash_location = game_state.get()['stash_location']
        self.mc.click_at_location(
            self.lf.get(Locations.DECORATIONS_EDIT_HIDEOUT_ARROW))
        self.mc.click_at_location(
            self.lf.get(Locations.DECORATIONS_EDIT_HIDEOUT_BUTTON))
        self.mc.click_at_location(
            self.lf.get(Locations.DECORATIONS_OPEN_BUTTON))

        # Sometimes the decorations take time to load.
        self.wait_for_decorations_to_load()

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
        game_state.update({'stash_location': stash_location})
        return StepStatus(True)

    def wait_for_decorations_to_load(self):
        ts = time.time()
        tm = TemplateMatcher(Template.from_registry(
            TemplateRegistry.DECORATIONS_UTILITIES_ARROW))
        while not tm.match(self.lf.get(Locations.DECORATIONS_UTILITIES_ARROW)):
            time.sleep(0.05)
