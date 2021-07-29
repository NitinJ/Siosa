import logging

from siosa.control.game_step import Step, StepStatus
from siosa.location.location_factory import Locations


class Error:
    STASH_NOT_OPEN = 0


class ChangeStashTab(Step):
    def __init__(self, index_to):
        """
        Args:
            index_to:
        """
        Step.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.index_to = index_to

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state
        state = self.game_state.get()

        if not state['stash_open']:
            return StepStatus(False, Error.STASH_NOT_OPEN)

        if self.index_to == 0:
            self.logger.debug("Moving stash tabs to index 0")
            self.mc.click_at_location(
                self.lf.get(Locations.STASH_FIRST_TAB_RIGHT_LIST))
            self.game_state.update({'open_stash_tab_index': self.index_to})
            return StepStatus(True)

        current_index = state['open_stash_tab_index']

        if self.index_to == current_index:
            self.logger.debug("Already at current stash tab({})".format(
                current_index))
            return StepStatus(True)

        self.logger.debug(
            "Moving stash tabs from index ({})->({})".format(
                current_index, self.index_to))

        key = 'right' if (self.index_to > current_index) else 'left'
        diff = abs(self.index_to - current_index)

        self.kc.hold_modifier('Ctrl')
        for i in range(0, diff):
            self.kc.keypress(key)
        self.kc.unhold_modifier('Ctrl')

        self.game_state.update({'open_stash_tab_index': self.index_to})
        return StepStatus(True)

