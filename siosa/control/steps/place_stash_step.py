import time

from siosa.control.game_step import Step
from siosa.location.location_factory import LocationFactory, Locations


class PlaceStash(Step):
    DECORATIONS_LOAD_TIME = 1.5

    """
    Places stash on the center of the screen. We cannot move to or get the stash
    co-ordinates so, we move the stash to the center of the screen.
    """
    def execute(self, game_state):
        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        self.mc.click_at_location(Locations.EDIT_HIDEOUT_ARROW)
        self.mc.click_at_location(Locations.EDIT_HIDEOUT_BUTTON)
        self.mc.click_at_location(Locations.OPEN_DECORATIONS_BUTTON)

        # Sometimes the decorations take time to load.
        time.sleep(PlaceStash.DECORATIONS_LOAD_TIME)

        self.mc.click_at_location(Locations.STASH_DECORATION)
        self.mc.click_at_location(Locations.CLOSE_DECORATIONS_BUTTON)
        stash_location = LocationFactory().create(
            Locations.SCREEN_CENTER.x1,
            Locations.SCREEN_CENTER.y1,
            Locations.SCREEN_CENTER.x2,
            Locations.SCREEN_CENTER.y2)
        self.mc.click_at_location(stash_location)
        game_state.update({'stash_location': stash_location})
        self.mc.click_at_location(Locations.EDIT_HIDEOUT_BUTTON)
        self.mc.click_at_location(Locations.EDIT_HIDEOUT_DOWN_ARROW)
