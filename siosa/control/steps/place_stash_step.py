import time

from siosa.control.game_step import Step
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
        stash_location = game_state.get()['stash_location']

        if stash_location is not None and stash_location.equals(
                self.lf.get(Locations.SCREEN_CENTER)):
            # Already at the center of the screen.
            return
        stash_location = self.lf.get(Locations.SCREEN_CENTER)

        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        self.mc.click_at_location(self.lf.get(Locations.EDIT_HIDEOUT_ARROW))
        self.mc.click_at_location(self.lf.get(Locations.EDIT_HIDEOUT_BUTTON))
        self.mc.click_at_location(
            self.lf.get(Locations.OPEN_DECORATIONS_BUTTON))

        # Sometimes the decorations take time to load.
        time.sleep(PlaceStash.DECORATIONS_LOAD_TIME)

        self.kc.keypress_with_modifiers(['ctrl', 'f'])
        time.sleep(PlaceStash.SEARCH_BOX_DELAY)

        self.kc.write('stash')
        self.mc.click_at_location(self.lf.get(Locations.STASH_DECORATION_AFTER_SEARCHING))
        self.mc.click_at_location(
            self.lf.get(Locations.CLOSE_DECORATIONS_BUTTON))
        self.mc.click_at_location(stash_location)
        self.mc.click_at_location(self.lf.get(Locations.EDIT_HIDEOUT_BUTTON))
        self.mc.click_at_location(
            self.lf.get(Locations.EDIT_HIDEOUT_DOWN_ARROW))

        game_state.update({'stash_location': stash_location})
