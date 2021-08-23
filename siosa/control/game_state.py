import logging
import threading

from siosa.data.zones import Zones


class GameState:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.state = {
            'stash_open': False,
            'inventory_open': False,
            'stash_location': None,
            'open_stash_tab_index': 0,
            'inventory': [],
            'inventory_empty': True,
            'players_in_hideout': [],
            'on_going_task': [],
            'current_zone': Zones.UNKNOWN
        }
        self.lock = threading.Lock()

    def update(self, state_dictionary={}):
        """
        Args:
            state_dictionary:
        """
        self.lock.acquire()
        self.state.update(state_dictionary)
        self.logger.info(
            "Updated game_state with {}".format(state_dictionary))
        self.lock.release()

    def get(self):
        self.lock.acquire()
        state = self.state.copy()
        self.lock.release()
        return state

    def __str__(self):
        s = ""
        for k, v in self.state.items():
            s = s + "{}: {}, ".format(str(k), str(v))
        return s
