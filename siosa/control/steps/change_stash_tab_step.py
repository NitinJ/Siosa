import logging
import time

from siosa.control.game_step import Step
from siosa.data.zones import Zones


class ChangeStashTab(Step):
    def __init__(self, game_state, index_to):
        Step.__init__(self, game_state)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.current_index = self.game_state.get()['open_stash_tab_index']
        self.index_to = index_to

    def execute(self):
        if not self.game_state.get()['stash_open']:
            raise Exception("Stash not open")
        if self.index_to == self.current_index:
            self.logger.debug(
                "Already at current stash tab({})".format(self.current_index))
            return
        self.logger.debug(
            "Moving stash tabs from index ({})->({})".format(self.current_index, self.index_to))
        key = 'right' if (self.index_to > self.current_index) else 'left'
        diff = abs(self.index_to - self.current_index)
        self.kc.hold_modifier('Ctrl')
        for i in range(0, diff):
            self.kc.keypress(key)
        self.kc.unhold_modifier('Ctrl')
        self.game_state.update({'open_stash_tab_index': self.index_to})
