import threading
import logging
import json

from data.zones import Zones
from common.enum_encoder import EnumEncoder
from location.location_factory import Locations

class GameState:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state = {
            'stash_open': False,
            'inventory_open': False,
            'stash_location': None,
            'inventory': [],
            'inventory_empty': True,
            'players_in_hideout': [],
            'on_going_task': [],
            'current_zone': Zones.HIDEOUT
        }
        self.lock = threading.Lock()
    
    def update(self, state_dictionary={}):
        self.lock.acquire()
        self.state.update(state_dictionary)
        self.logger.info("Updated game_state with {}".format(self.__str__()))
        self.lock.release()
    
    def get(self):
        self.lock.acquire()
        state = self.state.copy()
        self.lock.release()
        return state

    def __str__(self):
        s = ""
        for k,v in self.state.items():
            s = s + "{}: {}, ".format(str(k), str(v))
        return s