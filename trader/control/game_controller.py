from enum import Enum
import time
import logging

from window_controller import WindowController
from console_controller import ConsoleController
from common.singleton import Singleton
from data.zones import Zones

class GameController(Singleton):
    LOCATION_ENTRY_WAIT_TIME = 100

    def __init__(self, client_log_listener):
        super(GameController, self).__init__()
        self.logger = logging.getLogger(__name__)

        self.mouse_position = None
        self.is_stash_open = False
        self.player_position = None
        self.current_stash_tab = None
        self.current_zone = None
        self.inventory = []

        self.wc = WindowController()
        self.cc = ConsoleController()

        self.log_listener = client_log_listener
        self.location_queue = self.log_listener.location_change_event_queue

    def initialize(self):
        # Move to poe
        self.wc.move_to_poe()
        self.current_zone = Zones.HIDEOUT

        # Trying to get the player on the way point exactly.
        self.move_to_zone(Zones.METAMORPH)
        time.sleep(0.5)
        self.move_to_zone(Zones.HIDEOUT)

        # Open stash
        
        # Organize stash
        # Ready !
        pass

    def _wait_for_zone(self, zone):
        t1 = time.time()
        while True:
            t2 = time.time()
            if t2 - t1 > GameController.LOCATION_ENTRY_WAIT_TIME:
                return False
            if not self.location_queue.empty():
                location_change_event = self.location_queue.get()
                if location_change_event.zone == zone:
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
        self.cc.console_command("/" + str(zone.value))
        success = self._wait_for_zone(zone)
        if not success:
            raise Exception("Cannot travel to zone: {}".format(zone))
        self.logger.debug("Moved to zone {}".format(zone.value))
        self.current_zone = zone