import time

from control.game_step import Step
from location.location_factory import Locations, LocationFactory

class PlaceStash(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
    
    def execute(self):
        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        self.mc.click_at_location(Locations.EDIT_HIDEOUT_ARROW)
        self.mc.click_at_location(Locations.EDIT_HIDEOUT_BUTTON)
        self.mc.click_at_location(Locations.OPEN_DECORATIONS_BUTTON)
        
        # Sometimes the decorations take time to load.
        time.sleep(1.5)
        
        self.mc.click_at_location(Locations.STASH_DECORATION)
        self.mc.click_at_location(Locations.CLOSE_DECORATIONS_BUTTON)
        stash_location = LocationFactory.get_instance().create(
            Locations.SCREEN_CENTER.x1 - 100, 
            Locations.SCREEN_CENTER.y1 - 100, 
            Locations.SCREEN_CENTER.x2 - 100, 
            Locations.SCREEN_CENTER.y2 - 100)
        self.mc.click_at_location(stash_location)
        self.game_state.update({'stash_location': stash_location})
        self.mc.click_at_location(Locations.EDIT_HIDEOUT_BUTTON)
        self.mc.click_at_location(Locations.EDIT_HIDEOUT_DOWN_ARROW)
