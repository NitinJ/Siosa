import logging
import threading
import time

from siosa.common.decorations import abstractmethod


class GameStateUpdater(threading.Thread):
    def __init__(self, game_state):
        """
        Args:
            game_state:
        """
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.game_state = game_state

    @abstractmethod
    def run(self):
        pass


class PlayerInHideoutUpdater(GameStateUpdater):
    def __init__(self, game_state, log_listener):
        """
        Args:
            game_state:
            log_listener:
        """
        GameStateUpdater.__init__(self, game_state)
        self.log_listener = log_listener
        self.hideout_event_queue = self.log_listener.hideout_event_queue

    def run(self):
        self.logger.info("Starting GameStateUpdater: {}".format(self.__class__.__name__))
        while True:
            if not self.hideout_event_queue.empty():
                hideout_event = self.hideout_event_queue.get()
                players = self.game_state.get()['players_in_hideout']
                if hideout_event.joined and hideout_event.player not in players:
                    players.append(hideout_event.player)
                elif not hideout_event.joined and hideout_event.player in players:
                    players.remove(hideout_event.player)
                self.game_state.update({'players_in_hideout': players})
            time.sleep(0.05)


class ZoneUpdater(GameStateUpdater):
    def __init__(self, game_state, log_listener):
        """
        Args:
            game_state:
            log_listener:
        """
        GameStateUpdater.__init__(self, game_state)
        self.log_listener = log_listener
        self.location_change_event_queue = self.log_listener.location_change_event_queue

    def run(self):
        self.logger.info("Starting GameStateUpdater: {}".format(self.__class__.__name__))
        while True:
            if not self.location_change_event_queue.empty():
                self.game_state.update({
                    'current_zone': self.location_change_event_queue.get().zone
                })
            time.sleep(0.05)
