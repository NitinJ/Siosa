import time
import logging

from common.decorations import abstractmethod
from keyboard_controller import KeyboardController
from mouse_controller import MouseController
from console_controller import ConsoleController
from window_controller import WindowController
from location.location_factory import LocationFactory, Locations
from data.zones import Zones
from clipboard.poe_clipboard import PoeClipboard

class Step:
    def __init__(self, game_state):
        self.logger = logging.getLogger(__name__)
        self.game_state = game_state
        self.kc = KeyboardController()
        self.mc = MouseController(LocationFactory())
        self.cc = ConsoleController()
        self.wc = WindowController()

    @abstractmethod
    def execute(self):
        pass

class Wait(Step):
    def __init__(self, game_state, wait_time_in_secs):
        Step.__init__(self, game_state)
        self.wait_time_in_secs = wait_time_in_secs
    
    def execute(self):
        self.logger.info("Executing step: Wait")
        time.sleep(self.wait_time_in_secs)

class SwitchToGame(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
    
    def execute(self):
        self.logger.info("Executing step: SwitchToGame")
        self.wc.move_to_poe()

class OpenStash(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
    
    def execute(self):
        self.logger.info("Executing step: OpenStash")
        if not self.game_state.get()['stash_open']:
            game_state = self.game_state.get()
            self.mc.click_at_location(game_state['stash_location'])
            self.game_state.update({'stash_open': True})

class ChangeZone(Step):
    LOCATION_ENTRY_WAIT_TIME = 10
    def __init__(self, game_state, zone):
        Step.__init__(self, game_state)
        self.zone = zone
    
    def execute(self):
        self.logger.info("Executing step: ChangeZone")
        self.cc.console_command("/" + str(self.zone.value))
        success = self._wait_for_zone()
        if not success:
            raise Exception("Cannot travel to zone: {}".format(self.zone))
        self.logger.debug("Moved to zone {}".format(self.zone.value))
        self.game_state.update({'current_zone': Zones.HIDEOUT})

    def _wait_for_zone(self):
        self.logger.debug("Waiting to enter zone: {}".format(self.zone))
        t1 = time.time()
        while True:
            t2 = time.time()
            if t2 - t1 > ChangeZone.LOCATION_ENTRY_WAIT_TIME:
                self.logger.debug("Timed out while waiting to enter zone: {}".format(self.zone))
                return False
            state = self.game_state.get()
            if state['current_zone'] == self.zone:
                return True
            time.sleep(0.05)

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

class CloseAllWindows(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
    
    def execute(self):
        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        self.kc.hold_modifier('Ctrl')
        self.kc.keypress("`")
        self.kc.unhold_modifier('Ctrl')
        self.game_state.update({'stash_open': False, 'inventory_open': False})

class ScanInventory(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
        self.clipboard = PoeClipboard()
        self.items = []
    
    def execute(self):
        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        for col in xrange(0, 12):
            for row in xrange(0, 5):
                self.mc.move_mouse(self._get_location(row, col))
                item = self.clipboard.read_item_at_cursor()
                self.items.append(item)
        print self.items

    def _get_location(self, r, c):
        # Invent box size
        size = 55
        x = Locations.INVENTORY_0_0.x1
        y = Locations.INVENTORY_0_0.y1
        x2 = x + c * 55
        y2 = y + r * 55
        return LocationFactory.get_instance().create(x2, y2, x2, y2)