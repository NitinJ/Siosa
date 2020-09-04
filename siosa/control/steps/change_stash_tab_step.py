import logging

from siosa.control.game_step import Step


class ChangeStashTab(Step):
    def __init__(self, index_to):
        Step.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.index_to = index_to

    def execute(self, game_state):
        self.game_state = game_state
        state = self.game_state.get()

        if not state['stash_open']:
            raise Exception("Stash not open")

        current_index = state['open_stash_tab_index']

        if self.index_to == current_index:
            self.logger.debug("Already at current stash tab({})".format(
                current_index))
            return

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
