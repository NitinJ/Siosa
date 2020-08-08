from enum import Enum
import time

from .window_controller import WindowController
from .console_controller import ConsoleController
from common.singleton import Singleton

class Zone(Enum):
    HIDEOUT = 'hideout'
    MENAERIE = 'menagerie'
    DELVE = 'delve'
    HARVEST = 'harvest'
    METAMORPH = 'metamorph'

class GameController(Singleton):
    LOCATION_ENTRY_WAIT_TIME = 5

    def __init__(self, client_log_listener):
        super(GameController, self).__init__()

        self.mouse_position = None
        self.is_stash_open = False
        self.player_position = None
        self.current_stash_tab = None
        self.inventory = []

        self.wc = WindowController()
        self.cc = ConsoleController()

        self.log_listener = client_log_listener
        self.location_queue = self.log_listener.location_change_event_queue

    def initialize(self):
        # Move to poe
        self.wc.move_to_poe()

        # Trying to get the player to the way point exactly.
        self.move_to_zone(Zone.METAMORPH)
        success = self._wait_for_location(Zone.METAMORPH)
        if not success:
            raise Exception("Cannot travel to zone: {}".format(Zone.METAMORPH))
        # go to hideout
        
        # Open stash
        # Organize stash
        # Ready !
        pass

    def _wait_for_location(self, location):
        t1 = time.time()
        while True:
            t2 = time.time()
            if t2 - t1 > GameController.LOCATION_ENTRY_WAIT_TIME:
                return False
            if not self.location_queue.empty():
                location_change_event = self.location_queue.get()
                if location_change_event.location == location:
                    return True
            time.sleep(0.05)

    def _get_is_stash_open(self):
        pass
    
    def _open_stash(self):
        pass

    def _move_currency_in_invent_to_stash(self):
        pass

    def _open_stash_tab(self, tab_index):
        pass

    def _pickup_item_from_stash_tab(self, tab_index, stash_item):
        pass

    def _move_item_to_trade_window(self, inventory_item):
        pass

    def trade_item(self, trade):
        pass

    def move_to_zone(self, zone):
        self.cc.console_command("/" + zone)