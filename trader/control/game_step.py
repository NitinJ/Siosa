import time
import logging

from common.decorations import abstractmethod
from keyboard_controller import KeyboardController
from mouse_controller import MouseController
from console_controller import ConsoleController
from window_controller import WindowController
from location.location_factory import LocationFactory

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
            self.mc.move_to_screen_center()
            self.mc.click()

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