import threading

class GameState:
    def __init__(self):
        self.state = {
            'stash_open': False,
            'inventory': [],
            'inventory_empty': True,
            'players_in_hideout': [],
            'on_going_task': [],
            'current_zone': None
        }
        self.lock = threading.Lock()
    
    def update(self, state_dictionary={}):
        self.lock.acquire()
        self.state.update(state_dictionary)
        self.lock.release()
    
    def get(self):
        self.lock.acquire()
        state = self.state.copy()
        self.lock.release()
        return state